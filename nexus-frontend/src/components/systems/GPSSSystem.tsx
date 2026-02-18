import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import PricingCalculator from '../PricingCalculator';
import ComplianceChecker from '../ComplianceChecker';
import SuppliersTab from '../SuppliersTab';
import SubcontractorsTab from '../SubcontractorsTab';
import { PricingDashboard } from './PricingDashboard';
import { ProposalBioAnalyzer } from './ProposalBioAnalyzer';

interface GPSSSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface Opportunity {
  id: string;
  title: string;
  rfpNumber: string;
  agency: string;
  value: number;
  dueDate: string;
  source: 'Federal' | 'State' | 'Local' | 'Cooperative';
  sourcePortal: string;
  state: string;
  setAsideType: string;
  edwsbEligible: boolean;
  priorityScore: number;
  urgency: 'Critical' | 'High' | 'Medium' | 'Low';
  category: string;
  homeStatePriority: boolean;
  internalStatus: string;
}

interface Proposal {
  id: string;
  proposalName: string;
  opportunityId: string;
  rfpNumber: string;
  agency: string;
  value: number;
  status: string;
  generatedDate: string;
  sentDate?: string;
  dueDate: string;
  executiveSummary: string;
  technicalApproach: string;
  staffingPlan: string;
  pastPerformance: string;
  pricingTotal: number;
  pricingBreakdown: any;
  pricingJustification: string;
  complianceChecklist: any;
  recipients: any;
  // ProposalBio fields
  proposalBioScore?: number;
  proposalBioStatus?: string;
  proposalBioGate?: string;
  proposalBioBiohacks?: any[];
  proposalBioCriticalIssues?: any[];
}

const GPSSSystem: React.FC<GPSSSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  // Opportunities State
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [pipelineOpps, setPipelineOpps] = useState<any[]>([]);
  const [edwosbOpps, setEdwosbOpps] = useState<any[]>([]);
  const [homeStateOpps, setHomeStateOpps] = useState<any[]>([]);
  const [forecastOpps, setForecastOpps] = useState<any[]>([]);
  const [oppCounts, setOppCounts] = useState({ total: 0, pipeline: 0, edwosb: 0, home_state: 0, forecasts: 0, filtered_ineligible: 0 });
  const [activeView, setActiveView] = useState<'pipeline' | 'edwosb' | 'home_state' | 'forecasts' | 'all'>('pipeline');
  const [loading, setLoading] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [filters, setFilters] = useState({
    source: 'all',
    state: 'all',
    edwsbOnly: false,
    urgency: 'all',
    homeStatesOnly: false
  });

  // Proposals State
  const [proposals, setProposals] = useState<Proposal[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [proposalsLoading, setProposalsLoading] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [generatingProposal, setGeneratingProposal] = useState(false);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [editBuffer, setEditBuffer] = useState<string>('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  // RFP Analysis State
  const [rfpAnalysis, setRfpAnalysis] = useState<any>(null);

  // Opportunity Detail State
  const [expandedOppId, setExpandedOppId] = useState<string | null>(null);

  // Sub Matching State
  const [subMatchResults, setSubMatchResults] = useState<Record<string, any>>({});
  const [matchingSubsFor, setMatchingSubsFor] = useState<string | null>(null);
  const [miningGapsFor, setMiningGapsFor] = useState<string | null>(null);
  const [gapMineResults, setGapMineResults] = useState<Record<string, any>>({});

  // Pricing Calculator State
  const [showPricingCalculator, setShowPricingCalculator] = useState(false);
  const [pricingOpportunity, setPricingOpportunity] = useState<Opportunity | null>(null);

  // Compliance Checker State
  const [showComplianceChecker, setShowComplianceChecker] = useState(false);
  const [complianceRfpContent, setComplianceRfpContent] = useState('');

  // Contacts State
  const [contacts, setContacts] = useState<any[]>([]);
  const [contactsLoading, setContactsLoading] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState<any | null>(null);
  const [contactFormData, setContactFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    title: '',
    agency: '',
    department: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    source: 'Manual'
  });

  // Products State
  const [products, setProducts] = useState<any[]>([]);
  const [productsLoading, setProductsLoading] = useState(false);
  const [showProductModal, setShowProductModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [productSearch, setProductSearch] = useState('');
  const [productCategoryFilter, setProductCategoryFilter] = useState('all');
  const [expandedProductId, setExpandedProductId] = useState<string | null>(null);
  const [productFormData, setProductFormData] = useState({
    name: '',
    description: '',
    category: '',
    basePrice: 0,
    unit: 'each',
    serviceCategory: ''
  });

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'discovery', label: '🔍 Discovery' },
    { id: 'upload', label: '📄 Upload RFP' },
    { id: 'opportunities', label: '🎯 Opportunities' },
    { id: 'suppliers', label: '🏭 Suppliers' },
    { id: 'subcontractors', label: '👷 Subcontractors' },
    { id: 'proposals', label: '📝 Proposals' },
    { id: 'proposalbio', label: '🧬 ProposalBio™' },
    { id: 'contacts', label: '👥 Contacts' },
    { id: 'products', label: '📦 Products' },
    { id: 'pricing', label: '💰 Pricing System' },
    { id: 'analytics', label: '📈 Analytics' }
  ];

  // Fetch opportunities on mount
  useEffect(() => {
    fetchOpportunities();
  }, []);

  // Fetch dashboard stats when dashboard tab is active
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchOpportunities(); // Refresh opportunities for dashboard
    }
  }, [activeTab]);

  // Fetch contacts when contacts tab is active
  useEffect(() => {
    if (activeTab === 'contacts') {
      fetchContacts();
    }
  }, [activeTab]);

  // Fetch products when products tab is active
  useEffect(() => {
    if (activeTab === 'products') {
      fetchProducts();
    }
  }, [activeTab]);

  // Fetch proposals when proposals tab is active
  useEffect(() => {
    if (activeTab === 'proposals') {
      fetchProposals();
    }
  }, [activeTab]);

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      // Fetch from Airtable via backend with categorized data
      const response = await api.getGpssOpportunities();
      setOpportunities(response.opportunities || []);
      setPipelineOpps(response.pipeline || []);
      setEdwosbOpps(response.edwosb || []);
      setHomeStateOpps(response.home_state || []);
      setForecastOpps(response.forecasts || []);
      setOppCounts(response.counts || { total: 0, pipeline: 0, edwosb: 0, home_state: 0, forecasts: 0, filtered_ineligible: 0 });
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      setNotification({ message: 'Failed to load opportunities. Please try again.', type: 'error' });
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  // filteredOpportunities is now handled by displayedOpportunities via activeView

  // Use real backend counts
  const stats = {
    pipelineCount: oppCounts.pipeline,
    edwsbSetAsides: oppCounts.edwosb,
    homeStateOpps: oppCounts.home_state,
    forecastsCount: oppCounts.forecasts,
    totalEligible: oppCounts.total,
    filteredIneligible: oppCounts.filtered_ineligible,
    criticalUrgency: pipelineOpps.filter(o => {
      if (!o.dueDate) return false;
      const due = new Date(o.dueDate);
      const now = new Date();
      const daysLeft = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      return daysLeft <= 7 && daysLeft >= 0;
    }).length,
  };

  // Get the list to display based on active view
  const displayedOpportunities = (() => {
    switch (activeView) {
      case 'pipeline': return pipelineOpps;
      case 'edwosb': return edwosbOpps;
      case 'home_state': return homeStateOpps;
      case 'forecasts': return forecastOpps;
      case 'all': return opportunities;
    }
  })();

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value}`;
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'Critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'High': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Proposal Functions
  const fetchProposals = async () => {
    setProposalsLoading(true);
    try {
      const response = await api.getGpssProposals();
      setProposals(response.proposals || []);
    } catch (error) {
      console.error('Error fetching proposals:', error);
      setProposals([]);
    } finally {
      setProposalsLoading(false);
    }
  };

  const generateProposal = async (opportunity: Opportunity) => {
    setGeneratingProposal(true);
    try {
      // Step 1: Calculate intelligent pricing first
      showNotification('🤖 Calculating intelligent pricing...', 'success');
      const pricingResponse = await api.calculateIntelligentPricing(opportunity.id);
      
      if (pricingResponse.error) {
        showNotification(`⚠️ Pricing calculation failed, using estimated value...`, 'error');
      }

      // Step 2: Generate proposal with pricing data
      showNotification('📝 Generating proposal content...', 'success');
      const response = await api.generateQuote(opportunity.id);
      
      if (response.error) {
        showNotification(`❌ Error generating proposal: ${response.error}`, 'error');
        return;
      }

      // Use intelligent pricing if available, otherwise use AI's pricing
      const finalPricing = pricingResponse.error ? {
        total: response.pricing?.total || opportunity.value,
        breakdown: response.pricing?.breakdown || {},
        justification: response.pricing?.justification || ''
      } : {
        total: pricingResponse.recommended_price,
        breakdown: pricingResponse.cost_breakdown,
        justification: `${pricingResponse.justification}\n\nPricing Strategy: ${pricingResponse.pricing_strategy}\nWin Probability: ${pricingResponse.win_probability}%\nMarket Position: ${pricingResponse.market_position}\nRisk Assessment: ${pricingResponse.risk_assessment}`
      };

      // Create proposal object with intelligent pricing
      const newProposal: Proposal = {
        id: Date.now().toString(), // Temporary ID until saved to Airtable
        proposalName: `${opportunity.rfpNumber} - ${opportunity.agency}`,
        opportunityId: opportunity.id,
        rfpNumber: opportunity.rfpNumber,
        agency: opportunity.agency,
        value: finalPricing.total,
        status: 'Draft',
        generatedDate: new Date().toISOString(),
        dueDate: opportunity.dueDate,
        executiveSummary: response.executive_summary || '',
        technicalApproach: response.technical_approach || '',
        staffingPlan: response.staffing_plan || '',
        pastPerformance: response.past_performance || '',
        pricingTotal: finalPricing.total,
        pricingBreakdown: finalPricing.breakdown,
        pricingJustification: finalPricing.justification,
        complianceChecklist: response.compliance_checklist || {},
        recipients: response.recipients || {}
      };

      setSelectedProposal(newProposal);
      setShowProposalModal(true);
      showNotification('🎉 Proposal with intelligent pricing generated!', 'success');
      
    } catch (error) {
      showNotification('❌ Error generating proposal', 'error');
    } finally {
      setGeneratingProposal(false);
    }
  };

  const saveProposal = async (proposal: Proposal) => {
    try {
      // Save proposal to Airtable
      await api.saveGpssProposal(proposal);
      
      // TODO: Save pricing history for AI learning when endpoint is ready
      
      showNotification('✅ Proposal saved to Airtable!', 'success');
      setShowProposalModal(false);
      fetchProposals();
    } catch (error) {
      showNotification('❌ Error saving proposal', 'error');
    }
  };

  const exportProposalPDF = (proposal: Proposal) => {
    const pricingVal = proposal.pricingTotal || proposal.value || 0;
    const content = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${proposal.proposalName || 'Proposal'}</title>
<style>
  @page { margin: 1in; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a1a; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; }
  .header { border-bottom: 3px solid #1e40af; padding-bottom: 20px; margin-bottom: 30px; }
  .header h1 { color: #1e40af; font-size: 24px; margin: 0 0 8px 0; }
  .header .meta { color: #666; font-size: 13px; }
  .company { font-size: 14px; color: #1e40af; font-weight: bold; margin-top: 12px; }
  h2 { color: #1e40af; font-size: 16px; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-top: 30px; text-transform: uppercase; letter-spacing: 0.5px; }
  .section { margin-bottom: 20px; font-size: 13px; }
  .pricing-box { background: #f0fdf4; border: 2px solid #16a34a; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center; }
  .pricing-box .amount { font-size: 32px; font-weight: 900; color: #16a34a; }
  .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #1e40af; font-size: 11px; color: #666; text-align: center; }
  @media print { body { padding: 0; } }
</style></head><body>
<div class="header">
  <h1>${proposal.proposalName || 'Proposal'}</h1>
  <div class="meta">
    RFP: ${proposal.rfpNumber || 'N/A'} &nbsp;|&nbsp; Agency: ${proposal.agency || 'N/A'} &nbsp;|&nbsp; Due: ${proposal.dueDate || 'N/A'}
  </div>
  <div class="company">Dee Davis Inc. &mdash; EDWOSB Certified</div>
</div>

<h2>Executive Summary</h2>
<div class="section">${(proposal.executiveSummary || 'Not yet generated.').replace(/\n/g, '<br>')}</div>

<h2>Technical Approach</h2>
<div class="section">${(proposal.technicalApproach || 'Not yet generated.').replace(/\n/g, '<br>')}</div>

<h2>Staffing Plan</h2>
<div class="section">${(proposal.staffingPlan || 'Not yet generated.').replace(/\n/g, '<br>')}</div>

<h2>Past Performance</h2>
<div class="section">${(proposal.pastPerformance || 'Not yet generated.').replace(/\n/g, '<br>')}</div>

<h2>Pricing</h2>
<div class="pricing-box">
  <div class="amount">$${pricingVal.toLocaleString()}</div>
  <div style="font-size:12px;color:#666;margin-top:4px;">Total Proposed Price</div>
</div>
${proposal.pricingJustification ? `<div class="section" style="font-size:12px;">${proposal.pricingJustification.replace(/\n/g, '<br>')}</div>` : ''}

<div class="footer">
  <strong>Dee Davis Inc.</strong> &mdash; Economically Disadvantaged Woman-Owned Small Business (EDWOSB)<br>
  Generated ${new Date().toLocaleDateString()} via NEXUS GPSS
</div>
</body></html>`;

    const blob = new Blob([content], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${proposal.rfpNumber || 'Proposal'}_${proposal.agency || 'Draft'}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    showNotification('Proposal exported — open in browser and Print to PDF', 'success');
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      showNotification(`Selected: ${file.name}`, 'success');
    } else {
      showNotification('Please select a PDF file', 'error');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      showNotification(`Selected: ${file.name}`, 'success');
    } else {
      showNotification('Please drop a PDF file', 'error');
    }
  };

  const analyzeRfp = async () => {
    if (!selectedFile) return;
    setIsExtracting(true);
    setRfpAnalysis(null);
    try {
      const result = await api.uploadAndAnalyzeRfp(selectedFile);
      if (result.success) {
        setRfpAnalysis(result);
        showNotification(
          `RFP analyzed: ${result.analysis?.bid_recommendation?.decision || 'REVIEW'} (${result.analysis?.bid_recommendation?.score || 0}/100) — ${result.contacts_found} contacts found`,
          'success'
        );
        // Refresh opportunities since we created a new one
        fetchOpportunities();
      } else {
        showNotification(result.error || 'Analysis failed', 'error');
      }
    } catch (error: any) {
      console.error('RFP analysis error:', error);
      showNotification(error.message || 'Error analyzing RFP', 'error');
    } finally {
      setIsExtracting(false);
    }
  };

  // Contacts Functions
  const fetchContacts = async () => {
    setContactsLoading(true);
    try {
      const response = await api.getGpssContacts();
      setContacts(response.contacts || []);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      setContacts([]);
    } finally {
      setContactsLoading(false);
    }
  };

  const createContact = async () => {
    try {
      const response = await api.createGpssContact(contactFormData);
      if (response.contact) {
        showNotification('✅ Contact created!', 'success');
        setShowContactModal(false);
        resetContactForm();
        fetchContacts();
      }
    } catch (error) {
      showNotification('❌ Error creating contact', 'error');
    }
  };

  const updateContact = async (contactId: string) => {
    try {
      const response = await api.updateGpssContact(contactId, contactFormData);
      if (response.success) {
        showNotification('✅ Contact updated!', 'success');
        setShowContactModal(false);
        resetContactForm();
        fetchContacts();
      }
    } catch (error) {
      showNotification('❌ Error updating contact', 'error');
    }
  };

  const deleteContact = async (contactId: string) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) return;
    try {
      const response = await api.deleteGpssContact(contactId);
      if (response.success) {
        showNotification('✅ Contact deleted!', 'success');
        fetchContacts();
      }
    } catch (error) {
      showNotification('❌ Error deleting contact', 'error');
    }
  };

  const resetContactForm = () => {
    setContactFormData({
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      title: '',
      agency: '',
      department: '',
      address: '',
      city: '',
      state: '',
      zip: '',
      source: 'Manual'
    });
    setSelectedContact(null);
  };

  const openContactModal = (contact?: any) => {
    if (contact) {
      setSelectedContact(contact);
      setContactFormData({
        firstName: contact.firstName || '',
        lastName: contact.lastName || '',
        email: contact.email || '',
        phone: contact.phone || '',
        title: contact.title || '',
        agency: contact.agency || '',
        department: contact.department || '',
        address: contact.address || '',
        city: contact.city || '',
        state: contact.state || '',
        zip: contact.zip || '',
        source: contact.source || 'Manual'
      });
    } else {
      resetContactForm();
    }
    setShowContactModal(true);
  };

  // Products Functions
  const fetchProducts = async () => {
    setProductsLoading(true);
    try {
      const response = await api.getGpssProducts();
      setProducts(response.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    } finally {
      setProductsLoading(false);
    }
  };

  const createProduct = async () => {
    try {
      const response = await api.createGpssProduct(productFormData);
      if (response.product) {
        showNotification('✅ Product created!', 'success');
        setShowProductModal(false);
        resetProductForm();
        fetchProducts();
      }
    } catch (error) {
      showNotification('❌ Error creating product', 'error');
    }
  };

  const updateProduct = async (productId: string) => {
    try {
      const response = await api.updateGpssProduct(productId, productFormData);
      if (response.success) {
        showNotification('✅ Product updated!', 'success');
        setShowProductModal(false);
        resetProductForm();
        fetchProducts();
      }
    } catch (error) {
      showNotification('❌ Error updating product', 'error');
    }
  };

  const deleteProduct = async (productId: string) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      const response = await api.deleteGpssProduct(productId);
      if (response.success) {
        showNotification('✅ Product deleted!', 'success');
        fetchProducts();
      }
    } catch (error) {
      showNotification('❌ Error deleting product', 'error');
    }
  };

  const resetProductForm = () => {
    setProductFormData({
      name: '',
      description: '',
      category: '',
      basePrice: 0,
      unit: 'each',
      serviceCategory: ''
    });
    setSelectedProduct(null);
  };

  const openProductModal = (product?: any) => {
    if (product) {
      setSelectedProduct(product);
      setProductFormData({
        name: product.name || '',
        description: product.description || '',
        category: product.category || '',
        basePrice: product.basePrice || 0,
        unit: product.unit || 'each',
        serviceCategory: product.serviceCategory || ''
      });
    } else {
      resetProductForm();
    }
    setShowProductModal(true);
  };

  return (
    <div className="relative">
      {/* System Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* TAB: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">GPSS Dashboard</h2>
              <p className="text-gray-400">Government Prime Sales System • Pre-Award Pipeline • EDWOSB Certified</p>
            </div>

            {/* Enhanced Quick Stats - Clickable View Switchers */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <button 
                onClick={() => { setActiveView('pipeline'); setActiveTab('opportunities'); }}
                className={`text-left p-6 rounded-xl transition border-2 ${activeView === 'pipeline' ? 'border-blue-400 ring-2 ring-blue-400/30' : 'border-transparent'} bg-gradient-to-br from-blue-600 to-blue-800`}
              >
                <div className="text-3xl mb-2">🎯</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">My Pipeline</h3>
                <p className="text-4xl font-bold mb-1">{stats.pipelineCount}</p>
                <p className="text-sm text-white/70">Active Bids</p>
              </button>

              <button 
                onClick={() => { setActiveView('edwosb'); setActiveTab('opportunities'); }}
                className={`text-left p-6 rounded-xl transition border-2 ${activeView === 'edwosb' ? 'border-green-400 ring-2 ring-green-400/30' : 'border-transparent'} bg-gradient-to-br from-green-600 to-green-800`}
              >
                <div className="text-3xl mb-2">⭐</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">EDWOSB Set-Asides</h3>
                <p className="text-4xl font-bold mb-1">{stats.edwsbSetAsides}</p>
                <p className="text-sm text-white/70">Exclusive Access</p>
              </button>

              <button 
                onClick={() => { setActiveView('home_state'); setActiveTab('opportunities'); }}
                className={`text-left p-6 rounded-xl transition border-2 ${activeView === 'home_state' ? 'border-purple-400 ring-2 ring-purple-400/30' : 'border-transparent'} bg-gradient-to-br from-purple-600 to-purple-800`}
              >
                <div className="text-3xl mb-2">🏠</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">Home State</h3>
                <p className="text-4xl font-bold mb-1">{stats.homeStateOpps}</p>
                <p className="text-sm text-white/70">Michigan Opportunities</p>
              </button>

              <button 
                onClick={() => { setActiveView('forecasts'); setActiveTab('opportunities'); }}
                className={`text-left p-6 rounded-xl transition border-2 ${activeView === 'forecasts' ? 'border-yellow-400 ring-2 ring-yellow-400/30' : 'border-transparent'} bg-gradient-to-br from-yellow-600 to-yellow-800`}
              >
                <div className="text-3xl mb-2">🔮</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">Forecasts</h3>
                <p className="text-4xl font-bold mb-1">{stats.forecastsCount}</p>
                <p className="text-sm text-white/70">Upcoming Procurements</p>
              </button>

              <button 
                onClick={() => { setActiveView('all'); setActiveTab('opportunities'); }}
                className={`text-left p-6 rounded-xl transition border-2 ${activeView === 'all' ? 'border-gray-400 ring-2 ring-gray-400/30' : 'border-transparent'} bg-gradient-to-br from-gray-600 to-gray-800`}
              >
                <div className="text-3xl mb-2">📋</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">All Eligible</h3>
                <p className="text-4xl font-bold mb-1">{stats.totalEligible}</p>
                <p className="text-sm text-white/70">{stats.filteredIneligible} ineligible filtered</p>
              </button>
            </div>

            {/* PROACTIVE ALERTS - What needs attention NOW */}
            {(() => {
              const stepLabels: Record<number, string> = {
                0: 'Not started', 1: 'Review', 2: 'Go/No-Go', 3: 'Find Suppliers',
                4: 'Create RFQ', 5: 'Send RFQ', 6: 'Collect Quotes',
                7: 'Price & Markup', 8: 'Prepare Bid', 9: 'Final Review', 10: 'Submitted'
              };
              const nextAction: Record<number, string> = {
                0: 'Start reviewing this solicitation',
                1: 'Make a Go/No-Go decision',
                2: 'Find suppliers who can quote this',
                3: 'Generate an RFQ document',
                4: 'Send the RFQ to suppliers',
                5: 'Follow up — waiting on quotes',
                6: 'Select best quote and calculate markup',
                7: 'Prepare the bid submission package',
                8: 'Do final review before submitting',
                9: 'Submit the bid NOW',
                10: 'Submitted — awaiting award'
              };
              const now = new Date();
              const alerts = pipelineOpps
                .map((opp: any) => {
                  const step = opp.workflowStep || 0;
                  const due = opp.dueDate ? new Date(opp.dueDate) : null;
                  const daysLeft = due ? Math.ceil((due.getTime() - now.getTime()) / (1000*60*60*24)) : 999;
                  const urgency = daysLeft <= 1 ? 'critical' : daysLeft <= 3 ? 'urgent' : daysLeft <= 7 ? 'soon' : 'ok';
                  return { ...opp, step, daysLeft, urgency, stepLabel: stepLabels[step] || `Step ${step}`, action: nextAction[step] || 'Continue working' };
                })
                .filter((a: any) => a.step < 10 && a.daysLeft <= 7)
                .sort((a: any, b: any) => a.daysLeft - b.daysLeft);
              
              if (alerts.length === 0) return null;
              return (
                <div className="mb-6 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                  <div className="px-5 py-3 bg-red-900/30 border-b border-red-500/30 flex items-center justify-between">
                    <h3 className="font-bold text-red-400">Needs Your Attention ({alerts.length})</h3>
                    <button onClick={() => { setActiveView('pipeline'); setActiveTab('opportunities'); }} className="text-xs text-gray-400 hover:text-white">View All</button>
                  </div>
                  <div className="divide-y divide-gray-700/50">
                    {alerts.slice(0, 6).map((a: any) => (
                      <div key={a.id} className="px-5 py-3 flex items-center gap-4 hover:bg-gray-700/30 cursor-pointer" onClick={() => { setActiveView('pipeline'); setActiveTab('opportunities'); setExpandedOppId(a.id); }}>
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${a.urgency === 'critical' ? 'bg-red-500 animate-pulse' : a.urgency === 'urgent' ? 'bg-orange-500' : 'bg-yellow-500'}`} />
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm text-gray-200 truncate">{a.title}</p>
                          <p className="text-xs text-gray-400">{a.action}</p>
                        </div>
                        <div className="flex items-center gap-3 flex-shrink-0">
                          <div className="flex gap-0.5">
                            {[1,2,3,4,5,6,7,8,9,10].map((s: number) => (
                              <div key={s} className={`w-1.5 h-1.5 rounded-full ${s <= a.step ? 'bg-blue-500' : 'bg-gray-600'}`} />
                            ))}
                          </div>
                          <span className="text-[10px] text-gray-500 w-14 text-right">{a.stepLabel}</span>
                          <span className={`text-xs font-bold w-12 text-right ${a.urgency === 'critical' ? 'text-red-400' : a.urgency === 'urgent' ? 'text-orange-400' : 'text-yellow-400'}`}>
                            {a.daysLeft <= 0 ? 'OVERDUE' : a.daysLeft === 1 ? '1 day' : `${a.daysLeft} days`}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            {/* Recent Activity Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recent Opportunities */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">My Pipeline ({pipelineOpps.length})</h3>
                <div className="space-y-3">
                  {pipelineOpps.length === 0 ? (
                    <div className="text-gray-500 text-center py-6">No active bids in pipeline</div>
                  ) : (
                    pipelineOpps.slice(0, 5).map((opp: any) => (
                      <div key={opp.id} className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg hover:bg-gray-700 transition cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {opp.isEdwosb && <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/30 font-bold">EDWOSB</span>}
                              {opp.isHomeState && <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30 font-bold">HOME STATE</span>}
                              <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30">{opp.internalStatus}</span>
                            </div>
                            <h4 className="font-bold text-blue-400 line-clamp-1">{opp.title}</h4>
                            <p className="text-sm text-gray-400">{opp.agency}</p>
                          </div>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-400">{opp.rfpNumber}</span>
                          <span className="text-gray-400">{opp.setAsideType || 'Open'}</span>
                        </div>
                        {opp.dueDate && (
                          <div className="mt-2 text-xs text-gray-500">Due: {opp.dueDate}</div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Source Breakdown */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">📊 Opportunity Breakdown</h3>
                <div className="space-y-4">
                  <div className="bg-green-900/30 border border-green-700/50 px-4 py-3 rounded-lg cursor-pointer hover:bg-green-900/50 transition" onClick={() => { setActiveView('edwosb'); setActiveTab('opportunities'); }}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-green-400">EDWOSB / WOSB</span>
                      <span className="text-2xl font-bold">{stats.edwsbSetAsides}</span>
                    </div>
                    <div className="text-xs text-gray-400">Exclusive set-aside opportunities</div>
                  </div>

                  <div className="bg-purple-900/30 border border-purple-700/50 px-4 py-3 rounded-lg cursor-pointer hover:bg-purple-900/50 transition" onClick={() => { setActiveView('home_state'); setActiveTab('opportunities'); }}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-purple-400">Michigan (Home State)</span>
                      <span className="text-2xl font-bold">{stats.homeStateOpps}</span>
                    </div>
                    <div className="text-xs text-gray-400">Local advantage opportunities</div>
                  </div>

                  <div className="bg-yellow-900/30 border border-yellow-700/50 px-4 py-3 rounded-lg cursor-pointer hover:bg-yellow-900/50 transition" onClick={() => { setActiveView('forecasts'); setActiveTab('opportunities'); }}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-yellow-400">Forecasts</span>
                      <span className="text-2xl font-bold">{stats.forecastsCount}</span>
                    </div>
                    <div className="text-xs text-gray-400">Future planned procurements</div>
                  </div>

                  <div className="bg-gray-700/30 border border-gray-600/50 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-gray-400">Filtered Out (Ineligible)</span>
                      <span className="text-2xl font-bold text-gray-500">{stats.filteredIneligible}</span>
                    </div>
                    <div className="text-xs text-gray-500">SDVOSB, VOSB, HUBZone, 8(a), etc.</div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI System Status */}
            <div className="mt-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold mb-1">🤖 NEXUS Opportunity Mining Engine</h3>
                  <p className="text-sm text-gray-400">Monitoring 100+ federal, state, and local portals • AI-powered qualification</p>
                </div>
                <div className="flex items-center gap-2 bg-green-500/20 px-4 py-2 rounded-lg">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-400 font-semibold">Active</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: OPPORTUNITY DISCOVERY */}
        {activeTab === 'discovery' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">Opportunity Discovery Engine</h2>
              <p className="text-gray-400">Automated mining from SAM.gov, GovCon, State/Local portals, RSS feeds, and agency forecasts</p>
            </div>

            {/* Current Inventory from Airtable */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700/50 rounded-xl p-5 cursor-pointer hover:border-blue-400 transition" onClick={() => { setActiveView('pipeline'); setActiveTab('opportunities'); }}>
                <div className="text-sm font-semibold text-blue-400 mb-1">Pipeline</div>
                <div className="text-3xl font-black">{stats.pipelineCount}</div>
                <div className="text-xs text-gray-500">Active Bids</div>
              </div>
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700/50 rounded-xl p-5 cursor-pointer hover:border-green-400 transition" onClick={() => { setActiveView('edwosb'); setActiveTab('opportunities'); }}>
                <div className="text-sm font-semibold text-green-400 mb-1">EDWOSB</div>
                <div className="text-3xl font-black">{stats.edwsbSetAsides}</div>
                <div className="text-xs text-gray-500">Set-Asides</div>
              </div>
              <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/50 rounded-xl p-5 cursor-pointer hover:border-purple-400 transition" onClick={() => { setActiveView('home_state'); setActiveTab('opportunities'); }}>
                <div className="text-sm font-semibold text-purple-400 mb-1">Michigan</div>
                <div className="text-3xl font-black">{stats.homeStateOpps}</div>
                <div className="text-xs text-gray-500">Home State</div>
              </div>
              <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border border-yellow-700/50 rounded-xl p-5 cursor-pointer hover:border-yellow-400 transition" onClick={() => { setActiveView('forecasts'); setActiveTab('opportunities'); }}>
                <div className="text-sm font-semibold text-yellow-400 mb-1">Forecasts</div>
                <div className="text-3xl font-black">{stats.forecastsCount}</div>
                <div className="text-xs text-gray-500">Upcoming</div>
              </div>
              <div className="bg-gradient-to-br from-gray-800/50 to-gray-700/30 border border-gray-600/50 rounded-xl p-5 cursor-pointer hover:border-gray-400 transition" onClick={() => { setActiveView('all'); setActiveTab('opportunities'); }}>
                <div className="text-sm font-semibold text-gray-400 mb-1">All Eligible</div>
                <div className="text-3xl font-black">{stats.totalEligible}</div>
                <div className="text-xs text-gray-500">{stats.filteredIneligible} ineligible filtered</div>
              </div>
            </div>

            {/* Mining Sources - Manual Trigger Buttons */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold mb-1">Mining Sources</h3>
                  <p className="text-sm text-gray-400">These run automatically via cron, but you can trigger manually here</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {/* SAM.gov */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Searching SAM.gov API...', type: 'success' });
                      const response = await api.post('/gpss/mining/search-sam-api');
                      setNotification({ message: `SAM.gov: Found ${response.total_found}, imported ${response.imported}`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `SAM.gov error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🦅</span>
                  <span className="text-sm">SAM.gov</span>
                  <span className="text-[10px] text-blue-300/70">Federal API</span>
                </button>

                {/* EDWOSB Miner */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Mining EDWOSB/WOSB set-asides...', type: 'success' });
                      const response = await api.mineEdwosbOpportunities();
                      setNotification({ message: `EDWOSB: Found ${response.total_found}, imported ${response.imported} new`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `EDWOSB error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-green-600 hover:bg-green-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">⭐</span>
                  <span className="text-sm">EDWOSB</span>
                  <span className="text-[10px] text-green-300/70">Set-Aside Miner</span>
                </button>

                {/* GovCon */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Searching GovCon API...', type: 'success' });
                      const response = await api.post('/gpss/mining/search-govcon-api');
                      setNotification({ message: `GovCon: Found ${response.total_found}, imported ${response.imported}`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `GovCon error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-cyan-600 hover:bg-cyan-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">📊</span>
                  <span className="text-sm">GovCon</span>
                  <span className="text-[10px] text-cyan-300/70">Federal API</span>
                </button>

                {/* State/Local */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Mining state & local sources...', type: 'success' });
                      const response = await api.post('/gpss/mining/mine-state-local');
                      setNotification({ message: `State/Local: ${response.sources_checked} sources, imported ${response.imported}`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `State/Local error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-orange-600 hover:bg-orange-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🏛️</span>
                  <span className="text-sm">State/Local</span>
                  <span className="text-[10px] text-orange-300/70">Portal Scraping</span>
                </button>

                {/* RSS Feeds */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Checking RSS feeds...', type: 'success' });
                      const response = await api.post('/gpss/mining/check-rss-feeds');
                      setNotification({ message: `RSS: Found ${response.new_opportunities} from ${response.feeds_checked} feeds`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `RSS error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-purple-600 hover:bg-purple-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">📡</span>
                  <span className="text-sm">RSS Feeds</span>
                  <span className="text-[10px] text-purple-300/70">Gov RSS</span>
                </button>

                {/* Forecasts */}
                <button 
                  onClick={async () => {
                    try {
                      setNotification({ message: 'Mining agency forecasts (NASA, GSA, DHS, USAID...)...', type: 'success' });
                      const response = await api.mineAgencyForecasts();
                      setNotification({ message: `Forecasts: ${response.total_extracted || 0} extracted from agency pages`, type: 'success' });
                      setTimeout(() => fetchOpportunities(), 3000);
                    } catch (error: any) {
                      setNotification({ message: `Forecast error: ${error.message}`, type: 'error' });
                    }
                  }}
                  className="bg-yellow-600 hover:bg-yellow-700 px-4 py-4 rounded-lg font-bold transition flex flex-col items-center gap-2"
                >
                  <span className="text-2xl">🔮</span>
                  <span className="text-sm">Forecasts</span>
                  <span className="text-[10px] text-yellow-300/70">Agency Forecasts</span>
                </button>
              </div>
            </div>

            {/* Mining Sources Detail */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Mining Source Details</h3>
              <div className="space-y-3">
                {[
                  { name: 'SAM.gov API', description: 'Federal opportunities filtered for EDWOSB/WOSB/SB set-asides', schedule: 'Daily at 6 AM', icon: '🦅', type: 'API' },
                  { name: 'EDWOSB/WOSB Miner', description: 'Dedicated EDWOSB and WOSB set-aside opportunity scanner', schedule: 'Daily at 8 AM', icon: '⭐', type: 'API' },
                  { name: 'GovCon API', description: 'Secondary federal source — solicitations and combined synopsis', schedule: 'Via SAM.gov job', icon: '📊', type: 'API' },
                  { name: 'State/Local Portals', description: 'MI (SIGMA VSS), CA, TX, FL, NY + BidNet/PublicPurchase aggregators', schedule: 'Via scheduler', icon: '🏛️', type: 'Scraper' },
                  { name: 'RSS Feeds', description: 'Government RSS feeds for real-time opportunity alerts', schedule: 'Via scheduler', icon: '📡', type: 'RSS' },
                  { name: 'Agency Forecasts', description: 'NASA, GSA, DHS, USAID, Commerce, Treasury planned procurements', schedule: 'Daily at 7 AM', icon: '🔮', type: 'AI Extract' },
                  { name: 'ThomasNet (via Google CSE)', description: 'Supplier mining — searches ThomasNet indirectly for suppliers', schedule: 'On demand', icon: '🔧', type: 'Search' },
                ].map((source, idx) => (
                  <div key={idx} className="bg-gray-700/30 border border-gray-600/50 px-4 py-3 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <span className="text-xl">{source.icon}</span>
                      <div>
                        <div className="font-semibold text-sm">{source.name}</div>
                        <div className="text-xs text-gray-500">{source.description}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">{source.type}</span>
                      <span className="text-xs text-gray-500">{source.schedule}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Automation Status */}
            <div className="bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-green-400 mb-1">Automated Mining Active</h3>
                  <p className="text-gray-400 text-sm">
                    Mining runs automatically via cron schedule. EDWOSB/WOSB at 8 AM, Federal at 6 AM, Forecasts at 7 AM, 
                    Quote follow-ups 3x daily. Use the buttons above for manual scans when needed.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: UPLOAD RFP (Existing - unchanged) */}
        {activeTab === 'upload' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">Upload RFP / Solicitation</h2>
              <p className="text-gray-400">AI analyzes the full document: scope, requirements, contacts, compliance, and bid/no-bid recommendation</p>
            </div>

            {/* Upload Area - only show if no analysis yet */}
            {!rfpAnalysis && (
              <div className="bg-gray-800 rounded-xl p-8">
                <div 
                  className={`border-3 border-dashed ${isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-700/30'} p-12 rounded-xl text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800 transition`}
                  onClick={() => document.getElementById('fileInput')?.click()}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className="text-6xl mb-4">📄</div>
                  <h3 className="text-xl font-bold mb-2 text-blue-400">Drop RFP/Solicitation PDF here or click to browse</h3>
                  <p className="text-gray-400 mb-2">AI will analyze: Scope of Work, Requirements, Contacts, Compliance, Bid Recommendation</p>
                  <p className="text-gray-500 text-sm">Creates an opportunity record in your pipeline automatically</p>
                  <input 
                    type="file" 
                    id="fileInput" 
                    accept=".pdf,.txt,.doc,.docx" 
                    className="hidden"
                    onChange={handleFileSelect}
                  />
                </div>

                {selectedFile && (
                  <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg flex items-center justify-between">
                    <p className="text-green-400 font-semibold">
                      {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </p>
                    <button
                      onClick={() => { setSelectedFile(null); const fi = document.getElementById('fileInput') as HTMLInputElement; if (fi) fi.value = ''; }}
                      className="text-gray-400 hover:text-white text-sm"
                    >
                      Clear
                    </button>
                  </div>
                )}

                {selectedFile && !isExtracting && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={analyzeRfp}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-bold text-lg transition"
                    >
                      Analyze RFP with AI
                    </button>
                  </div>
                )}

                {isExtracting && (
                  <div className="mt-6">
                    <div className="bg-blue-900/30 border border-blue-700 p-6 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                        <div>
                          <h4 className="font-bold text-blue-400 mb-1">Analyzing RFP...</h4>
                          <p className="text-sm text-gray-400">Extracting scope, requirements, contacts, compliance items, and generating bid recommendation</p>
                          <p className="text-xs text-gray-500 mt-1">This may take 15-30 seconds for large documents</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Analysis Results */}
            {rfpAnalysis && (
              <div className="space-y-6">
                {/* Header with actions */}
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold">{rfpAnalysis.analysis?.solicitation_info?.title || rfpAnalysis.document_name}</h3>
                    <p className="text-gray-400 text-sm">{rfpAnalysis.document_name} — {rfpAnalysis.pages_read} pages analyzed</p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => { setRfpAnalysis(null); setSelectedFile(null); const fi = document.getElementById('fileInput') as HTMLInputElement; if (fi) fi.value = ''; }}
                      className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-semibold text-sm transition"
                    >
                      Upload Another
                    </button>
                    {rfpAnalysis.opportunity_id && (
                      <button
                        onClick={() => { setActiveView('pipeline'); setActiveTab('opportunities'); }}
                        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold text-sm transition"
                      >
                        View in Pipeline
                      </button>
                    )}
                  </div>
                </div>

                {/* Bid Recommendation Banner */}
                {rfpAnalysis.analysis?.bid_recommendation && (() => {
                  const rec = rfpAnalysis.analysis.bid_recommendation;
                  const isGo = rec.decision === 'GO';
                  const isNoGo = rec.decision === 'NO-GO';
                  return (
                    <div className={`rounded-xl p-6 border ${isGo ? 'bg-green-900/20 border-green-500/50' : isNoGo ? 'bg-red-900/20 border-red-500/50' : 'bg-yellow-900/20 border-yellow-500/50'}`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">{isGo ? '✅' : isNoGo ? '❌' : '⚠️'}</span>
                          <div>
                            <div className={`text-2xl font-black ${isGo ? 'text-green-400' : isNoGo ? 'text-red-400' : 'text-yellow-400'}`}>
                              {rec.decision}
                            </div>
                            <div className="text-sm text-gray-400">Bid Recommendation</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-3xl font-black">{rec.score}<span className="text-lg text-gray-400">/100</span></div>
                          <div className="text-xs text-gray-400">Fit Score</div>
                        </div>
                      </div>
                      <p className="text-gray-300 mb-3">{rec.reasoning}</p>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs font-semibold text-green-400 mb-1">STRENGTHS</div>
                          <ul className="text-sm text-gray-400 space-y-1">
                            {(rec.strengths || []).map((s: string, i: number) => <li key={i}>+ {s}</li>)}
                          </ul>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-red-400 mb-1">CONCERNS</div>
                          <ul className="text-sm text-gray-400 space-y-1">
                            {(rec.concerns || []).map((c: string, i: number) => <li key={i}>- {c}</li>)}
                          </ul>
                        </div>
                      </div>
                      <div className="mt-3 flex gap-4 text-xs text-gray-500">
                        <span>Effort: <strong>{rec.effort_level}</strong></span>
                        <span>Competitive Position: <strong>{rec.competitive_position}</strong></span>
                      </div>
                    </div>
                  );
                })()}

                {/* Solicitation Info + Scope side by side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Solicitation Info */}
                  {rfpAnalysis.analysis?.solicitation_info && (
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h4 className="text-lg font-bold mb-4">Solicitation Details</h4>
                      <div className="space-y-3">
                        {[
                          { label: 'RFP Number', value: rfpAnalysis.analysis.solicitation_info.rfp_number },
                          { label: 'Agency', value: rfpAnalysis.analysis.solicitation_info.agency },
                          { label: 'Deadline', value: rfpAnalysis.analysis.solicitation_info.deadline },
                          { label: 'Set-Aside', value: rfpAnalysis.analysis.solicitation_info.set_aside_type },
                          { label: 'NAICS', value: Array.isArray(rfpAnalysis.analysis.solicitation_info.naics_codes) ? rfpAnalysis.analysis.solicitation_info.naics_codes.join(', ') : rfpAnalysis.analysis.solicitation_info.naics_codes },
                          { label: 'Est. Value', value: rfpAnalysis.analysis.solicitation_info.estimated_value },
                          { label: 'Contract Type', value: rfpAnalysis.analysis.solicitation_info.contract_type },
                          { label: 'Location', value: rfpAnalysis.analysis.solicitation_info.performance_location },
                          { label: 'State', value: rfpAnalysis.analysis.solicitation_info.state },
                          { label: 'Period', value: rfpAnalysis.analysis.solicitation_info.period_of_performance },
                        ].filter(item => item.value).map((item, idx) => (
                          <div key={idx} className="flex justify-between items-start">
                            <span className="text-gray-500 text-sm w-28 shrink-0">{item.label}</span>
                            <span className="text-gray-200 text-sm text-right">{item.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Scope of Work */}
                  {rfpAnalysis.analysis?.scope_of_work && (
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h4 className="text-lg font-bold mb-4">Scope of Work</h4>
                      <p className="text-gray-300 text-sm mb-4">{rfpAnalysis.analysis.scope_of_work.summary}</p>
                      
                      {rfpAnalysis.analysis.scope_of_work.key_deliverables?.length > 0 && (
                        <div className="mb-4">
                          <div className="text-xs font-semibold text-blue-400 mb-2">KEY DELIVERABLES</div>
                          <ul className="space-y-1">
                            {rfpAnalysis.analysis.scope_of_work.key_deliverables.map((d: string, i: number) => (
                              <li key={i} className="text-sm text-gray-400 flex items-start gap-2">
                                <span className="text-blue-400 mt-0.5">-</span> {d}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {rfpAnalysis.analysis.scope_of_work.line_items?.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-purple-400 mb-2">LINE ITEMS</div>
                          <div className="space-y-1">
                            {rfpAnalysis.analysis.scope_of_work.line_items.map((item: any, i: number) => (
                              <div key={i} className="text-sm text-gray-400 bg-gray-700/50 px-3 py-2 rounded flex justify-between">
                                <span>{item.item}</span>
                                <span className="text-gray-500">{item.quantity ? `${item.quantity} ${item.unit || ''}` : ''}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Compliance + Contacts side by side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Compliance Requirements */}
                  {rfpAnalysis.analysis?.compliance_requirements && (
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h4 className="text-lg font-bold mb-4">Compliance Requirements</h4>
                      <div className="space-y-4">
                        {rfpAnalysis.analysis.compliance_requirements.required_documents?.length > 0 && (
                          <div>
                            <div className="text-xs font-semibold text-yellow-400 mb-2">REQUIRED DOCUMENTS</div>
                            <ul className="space-y-1">
                              {rfpAnalysis.analysis.compliance_requirements.required_documents.map((d: string, i: number) => (
                                <li key={i} className="text-sm text-gray-400 flex items-center gap-2">
                                  <span className="w-4 h-4 border border-gray-600 rounded flex-shrink-0"></span> {d}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {rfpAnalysis.analysis.compliance_requirements.required_certifications?.length > 0 && (
                          <div>
                            <div className="text-xs font-semibold text-green-400 mb-2">CERTIFICATIONS NEEDED</div>
                            <ul className="space-y-1">
                              {rfpAnalysis.analysis.compliance_requirements.required_certifications.map((c: string, i: number) => (
                                <li key={i} className="text-sm text-gray-400">- {c}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {rfpAnalysis.analysis.compliance_requirements.insurance_requirements && (
                          <div>
                            <div className="text-xs font-semibold text-orange-400 mb-1">INSURANCE</div>
                            <p className="text-sm text-gray-400">{rfpAnalysis.analysis.compliance_requirements.insurance_requirements}</p>
                          </div>
                        )}
                        {rfpAnalysis.analysis.compliance_requirements.bonding_requirements && (
                          <div>
                            <div className="text-xs font-semibold text-orange-400 mb-1">BONDING</div>
                            <p className="text-sm text-gray-400">{rfpAnalysis.analysis.compliance_requirements.bonding_requirements}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Contacts */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h4 className="text-lg font-bold mb-4">Contacts Extracted ({rfpAnalysis.contacts_found})</h4>
                    {rfpAnalysis.analysis?.contacts?.length > 0 ? (
                      <div className="space-y-3">
                        {rfpAnalysis.analysis.contacts.map((contact: any, idx: number) => (
                          <div key={idx} className="bg-gray-700/50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-semibold text-sm">{contact.name}</span>
                              <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">{contact.role}</span>
                            </div>
                            <div className="text-xs text-gray-400">{contact.title}</div>
                            {contact.email && <div className="text-xs text-blue-400 mt-1">{contact.email}</div>}
                            {contact.phone && <div className="text-xs text-gray-500">{contact.phone}</div>}
                          </div>
                        ))}
                        <p className="text-xs text-gray-500">{rfpAnalysis.contacts_stored} contacts saved to Airtable</p>
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">No contacts found in document</p>
                    )}
                  </div>
                </div>

                {/* Evaluation Criteria */}
                {rfpAnalysis.analysis?.evaluation_criteria?.length > 0 && (
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h4 className="text-lg font-bold mb-4">Evaluation Criteria</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {rfpAnalysis.analysis.evaluation_criteria.map((criteria: any, idx: number) => (
                        <div key={idx} className="bg-gray-700/50 rounded-lg p-4">
                          <div className="font-semibold text-sm text-blue-400 mb-1">{criteria.factor}</div>
                          {criteria.weight && <div className="text-xs text-yellow-400 mb-2">Weight: {criteria.weight}</div>}
                          <div className="text-xs text-gray-400">{criteria.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Created in Airtable confirmation */}
                {rfpAnalysis.opportunity_id && (
                  <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4 flex items-center gap-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <div className="font-semibold text-green-400">Opportunity Created in Pipeline</div>
                      <div className="text-sm text-gray-400">Record ID: {rfpAnalysis.opportunity_id} — View in Opportunities tab to take action</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: OPPORTUNITIES - ENHANCED */}
        {activeTab === 'opportunities' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">
                  {activeView === 'pipeline' && '🎯 My Pipeline'}
                  {activeView === 'edwosb' && '⭐ EDWOSB / WOSB Set-Asides'}
                  {activeView === 'home_state' && '🏠 Michigan Opportunities'}
                  {activeView === 'forecasts' && '🔮 Forecasted Procurements'}
                  {activeView === 'all' && '📋 All Eligible Opportunities'}
                </h2>
                <p className="text-gray-400">
                  {activeView === 'pipeline' && 'Your active bids and pursuits'}
                  {activeView === 'edwosb' && 'Exclusive EDWOSB/WOSB set-aside opportunities'}
                  {activeView === 'home_state' && 'Opportunities in Michigan — local advantage'}
                  {activeView === 'forecasts' && 'Future planned procurements from agency forecasts'}
                  {activeView === 'all' && `${stats.totalEligible} eligible • ${stats.filteredIneligible} ineligible filtered out`}
                </p>
              </div>
              <button 
                onClick={fetchOpportunities}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                Refresh
              </button>
            </div>

            {/* VIEW SWITCHER */}
            <div className="flex gap-2 mb-6 flex-wrap">
              <button onClick={() => setActiveView('pipeline')} className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${activeView === 'pipeline' ? 'bg-blue-600 text-white ring-2 ring-blue-400/50' : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'}`}>
                Pipeline ({oppCounts.pipeline})
              </button>
              <button onClick={() => setActiveView('edwosb')} className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${activeView === 'edwosb' ? 'bg-green-600 text-white ring-2 ring-green-400/50' : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'}`}>
                EDWOSB ({oppCounts.edwosb})
              </button>
              <button onClick={() => setActiveView('home_state')} className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${activeView === 'home_state' ? 'bg-purple-600 text-white ring-2 ring-purple-400/50' : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'}`}>
                Michigan ({oppCounts.home_state})
              </button>
              <button onClick={() => setActiveView('forecasts')} className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${activeView === 'forecasts' ? 'bg-yellow-600 text-white ring-2 ring-yellow-400/50' : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'}`}>
                Forecasts ({oppCounts.forecasts})
              </button>
              <button onClick={() => setActiveView('all')} className={`px-4 py-2 rounded-lg font-semibold text-sm transition ${activeView === 'all' ? 'bg-gray-500 text-white ring-2 ring-gray-400/50' : 'bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-white'}`}>
                All ({oppCounts.total})
              </button>
            </div>

            {/* OPPORTUNITIES TABLE */}
            <div className="bg-gray-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Opportunity</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Set-Aside</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Agency</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Due Date</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-500">Loading opportunities...</td></tr>
                    ) : displayedOpportunities.length === 0 ? (
                      <tr><td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        No opportunities in this view. 
                        {activeView === 'pipeline' && ' Your active bids will show here.'}
                        {activeView === 'edwosb' && ' No EDWOSB/WOSB set-asides found.'}
                        {activeView === 'home_state' && ' No Michigan opportunities found.'}
                        {activeView === 'forecasts' && ' No forecasted procurements yet.'}
                      </td></tr>
                    ) : displayedOpportunities.map((opp: any) => (
                      <React.Fragment key={opp.id}>
                        <tr 
                          className={`border-t border-gray-700 hover:bg-gray-700/50 cursor-pointer ${expandedOppId === opp.id ? 'bg-gray-700/30' : ''}`}
                          onClick={() => setExpandedOppId(expandedOppId === opp.id ? null : opp.id)}
                        >
                          <td className="px-6 py-4">
                            <div className="flex items-start gap-2 mb-1">
                              {opp.isEdwosb && (
                                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/30 font-bold">EDWOSB</span>
                              )}
                              {opp.isHomeState && (
                                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30 font-bold">HOME</span>
                              )}
                              {opp.isForecast && (
                                <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded border border-yellow-500/30 font-bold">FORECAST</span>
                              )}
                            </div>
                            <div className="font-bold text-blue-400 line-clamp-2">{opp.title}</div>
                            <div className="text-sm text-gray-400">{opp.rfpNumber}</div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="font-semibold text-purple-400 text-sm">{opp.setAsideType || 'Open'}</div>
                            <div className="text-xs text-gray-500 mt-1">{opp.state}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-300 text-sm">{opp.agency}</td>
                          <td className="px-6 py-4">
                            <div className="text-gray-300 text-sm">{opp.dueDate || 'N/A'}</div>
                          </td>
                          <td className="px-6 py-4">
                            {opp.workflowStep > 0 ? (
                              <div className="min-w-[140px]">
                                <div className="flex items-center gap-0.5 mb-1">
                                  {[1,2,3,4,5,6,7,8,9,10].map(s => (
                                    <div key={s} className={`h-1.5 flex-1 rounded-full ${
                                      s <= opp.workflowStep
                                        ? s <= 3 ? 'bg-blue-500' : s <= 6 ? 'bg-yellow-500' : s <= 9 ? 'bg-purple-500' : 'bg-green-500'
                                        : 'bg-gray-600'
                                    }`} />
                                  ))}
                                </div>
                                <p className="text-[10px] font-bold text-gray-300">
                                  {opp.workflowStep === 1 && 'Review'}
                                  {opp.workflowStep === 2 && 'Go/No-Go'}
                                  {opp.workflowStep === 3 && 'Find Suppliers'}
                                  {opp.workflowStep === 4 && 'RFQ Created'}
                                  {opp.workflowStep === 5 && 'RFQ Sent'}
                                  {opp.workflowStep === 6 && 'Awaiting Quotes'}
                                  {opp.workflowStep === 7 && 'Pricing'}
                                  {opp.workflowStep === 8 && 'Preparing Bid'}
                                  {opp.workflowStep === 9 && 'Final Review'}
                                  {opp.workflowStep === 10 && 'Submitted'}
                                </p>
                              </div>
                            ) : (
                              <span className="bg-gray-600 text-gray-300 px-2 py-1 rounded-full text-xs font-semibold">
                                {opp.internalStatus || 'New'}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-gray-500 text-sm">
                            {expandedOppId === opp.id ? '▲' : '▼'}
                          </td>
                        </tr>

                        {/* Expanded Detail Row */}
                        {expandedOppId === opp.id && (
                          <tr className="border-t border-gray-600/50">
                            <td colSpan={6} className="px-6 py-5 bg-gray-750/50">
                              {/* Workflow Step Bar */}
                              <div className="mb-5 bg-gray-800/80 rounded-lg p-3">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-bold text-gray-400">WORKFLOW</span>
                                  <span className="text-[10px] text-gray-500">Step {opp.workflowStep || 0} of 10</span>
                                </div>
                                <div className="flex gap-1">
                                  {[
                                    { step: 1, label: 'Review' },
                                    { step: 2, label: 'Go/No-Go' },
                                    { step: 3, label: 'Find Suppliers' },
                                    { step: 4, label: 'Create RFQ' },
                                    { step: 5, label: 'Send RFQ' },
                                    { step: 6, label: 'Collect Quotes' },
                                    { step: 7, label: 'Price & Markup' },
                                    { step: 8, label: 'Prepare Bid' },
                                    { step: 9, label: 'Final Review' },
                                    { step: 10, label: 'Submit' },
                                  ].map(({ step, label }) => {
                                    const current = opp.workflowStep || 0;
                                    const isComplete = step < current;
                                    const isCurrent = step === current;
                                    const isNext = step === current + 1;
                                    return (
                                      <button
                                        key={step}
                                        onClick={async (e) => {
                                          e.stopPropagation();
                                          try {
                                            await api.put(`/gpss/opportunities/${opp.id}`, { workflowStep: step });
                                            showNotification(`Step ${step}: ${label}`, 'success');
                                            fetchOpportunities();
                                          } catch { showNotification('Failed to update step', 'error'); }
                                        }}
                                        className={`flex-1 py-1.5 rounded text-[9px] font-bold transition leading-tight ${
                                          isComplete ? 'bg-green-600/80 text-white' :
                                          isCurrent ? 'bg-blue-600 text-white ring-2 ring-blue-400/60' :
                                          isNext ? 'bg-gray-600 text-gray-300 hover:bg-blue-600/50 hover:text-white ring-1 ring-dashed ring-blue-500/40' :
                                          'bg-gray-700/50 text-gray-500 hover:bg-gray-600 hover:text-gray-300'
                                        }`}
                                      >
                                        {label}
                                      </button>
                                    );
                                  })}
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {/* Details Column */}
                                <div className="space-y-3">
                                  <h4 className="font-bold text-sm text-gray-300 mb-2">Details</h4>
                                  {opp.naicsCodes && (
                                    <div><span className="text-xs text-gray-500">NAICS:</span> <span className="text-xs text-gray-300">{opp.naicsCodes}</span></div>
                                  )}
                                  {opp.category && (
                                    <div><span className="text-xs text-gray-500">Category:</span> <span className="text-xs text-gray-300">{opp.category}</span></div>
                                  )}
                                  {opp.contractingOfficer && (
                                    <div><span className="text-xs text-gray-500">CO:</span> <span className="text-xs text-gray-300">{opp.contractingOfficer}</span></div>
                                  )}
                                  {opp.priority && (
                                    <div><span className="text-xs text-gray-500">Priority:</span> <span className="text-xs text-gray-300">{opp.priority}</span></div>
                                  )}
                                  {opp.sourceUrl && (
                                    <a href={opp.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:underline block">
                                      View Original Posting
                                    </a>
                                  )}
                                </div>

                                {/* Notes / AI Recommendation */}
                                <div>
                                  <h4 className="font-bold text-sm text-gray-300 mb-2">Notes</h4>
                                  <p className="text-xs text-gray-400 whitespace-pre-wrap max-h-32 overflow-y-auto">
                                    {opp.notes || opp.aiRecommendation || 'No notes yet'}
                                  </p>
                                </div>

                                {/* Actions */}
                                <div>
                                  <h4 className="font-bold text-sm text-gray-300 mb-2">Actions</h4>
                                  <div className="flex flex-wrap gap-2">
                                    <button 
                                      onClick={(e) => { e.stopPropagation(); setPricingOpportunity(opp); setShowPricingCalculator(true); }}
                                      className="bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg font-semibold text-xs transition"
                                    >
                                      Calculate Pricing
                                    </button>
                                    <button 
                                      onClick={(e) => { e.stopPropagation(); generateProposal(opp); }}
                                      disabled={generatingProposal}
                                      className={`${generatingProposal ? 'bg-gray-600 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'} px-3 py-2 rounded-lg font-semibold text-xs transition`}
                                    >
                                      {generatingProposal ? 'Generating...' : 'Generate Proposal'}
                                    </button>
                                    <button 
                                      onClick={async (e) => {
                                        e.stopPropagation();
                                        try {
                                          showNotification('Finding matching suppliers...', 'success');
                                          await api.post('/gpss/auto-quote/find-suppliers', { opportunity_id: opp.id });
                                          showNotification('Suppliers matched — check Suppliers tab', 'success');
                                        } catch (err: any) {
                                          showNotification(err.message || 'Error finding suppliers', 'error');
                                        }
                                      }}
                                      className="bg-cyan-600 hover:bg-cyan-700 px-3 py-2 rounded-lg font-semibold text-xs transition"
                                    >
                                      Find Suppliers
                                    </button>
                                    <button 
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        setComplianceRfpContent(opp.title + '\n' + (opp.notes || ''));
                                        setShowComplianceChecker(true);
                                      }}
                                      className="bg-yellow-600 hover:bg-yellow-700 px-3 py-2 rounded-lg font-semibold text-xs transition"
                                    >
                                      Compliance Check
                                    </button>
                                    <button 
                                      onClick={async (e) => {
                                        e.stopPropagation();
                                        setMatchingSubsFor(opp.id);
                                        try {
                                          showNotification('AI is analyzing opportunity & matching subcontractors...', 'success');
                                          const resp = await api.post(`/gpss/opportunities/${opp.id}/match-subs`, {});
                                          setSubMatchResults(prev => ({ ...prev, [opp.id]: resp }));
                                          showNotification(`Found ${resp.matches_found || 0} matching subcontractors`, 'success');
                                        } catch (err: any) {
                                          showNotification(err.message || 'Error matching subs', 'error');
                                        } finally {
                                          setMatchingSubsFor(null);
                                        }
                                      }}
                                      disabled={matchingSubsFor === opp.id}
                                      className={`${matchingSubsFor === opp.id ? 'bg-purple-800 cursor-wait animate-pulse' : 'bg-purple-600 hover:bg-purple-700'} px-3 py-2 rounded-lg font-semibold text-xs transition`}
                                    >
                                      {matchingSubsFor === opp.id ? 'Matching...' : 'Match Subcontractors'}
                                    </button>
                                  </div>
                                </div>
                              </div>

                              {/* Sub Match Results Panel */}
                              {subMatchResults[opp.id] && subMatchResults[opp.id].analysis && (
                                <div className="mt-4 border-t border-gray-600 pt-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h4 className="font-bold text-sm text-purple-300 flex items-center gap-2">
                                      Subcontractor Matches
                                      <span className="bg-purple-600/30 px-2 py-0.5 rounded text-xs text-purple-200">
                                        {subMatchResults[opp.id].matches_found} found from {subMatchResults[opp.id].total_subs_evaluated} evaluated
                                      </span>
                                    </h4>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); setSubMatchResults(prev => { const n = {...prev}; delete n[opp.id]; return n; }); }}
                                      className="text-xs text-gray-500 hover:text-gray-300"
                                    >Dismiss</button>
                                  </div>
                                  
                                  {/* Summary & Recommendation */}
                                  <div className="bg-gray-800 rounded-lg p-3 mb-3">
                                    <p className="text-xs text-gray-300 mb-2">{subMatchResults[opp.id].analysis.opportunity_summary}</p>
                                    <div className="flex flex-wrap gap-2 mb-2">
                                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                                        subMatchResults[opp.id].analysis.partner_recommendation === 'self_perform' ? 'bg-green-600/30 text-green-300' :
                                        subMatchResults[opp.id].analysis.partner_recommendation === 'need_supplier' ? 'bg-cyan-600/30 text-cyan-300' :
                                        'bg-purple-600/30 text-purple-300'
                                      }`}>
                                        {subMatchResults[opp.id].analysis.partner_recommendation === 'self_perform' ? 'Can Self-Perform' :
                                         subMatchResults[opp.id].analysis.partner_recommendation === 'need_supplier' ? 'Need Supplier (Product)' :
                                         'Subcontractor Recommended'}
                                      </span>
                                      {subMatchResults[opp.id].analysis.self_perform_percentage > 0 && (
                                        <span className="text-xs px-2 py-1 rounded-full bg-gray-700 text-gray-300">
                                          Self-perform: {subMatchResults[opp.id].analysis.self_perform_percentage}%
                                        </span>
                                      )}
                                    </div>
                                    <p className="text-xs text-gray-400">{subMatchResults[opp.id].analysis.reasoning}</p>
                                  </div>

                                  {/* Required Capabilities */}
                                  {subMatchResults[opp.id].analysis.required_capabilities?.length > 0 && (
                                    <div className="mb-3">
                                      <p className="text-xs text-gray-500 mb-1">Required Capabilities:</p>
                                      <div className="flex flex-wrap gap-1">
                                        {subMatchResults[opp.id].analysis.required_capabilities.map((cap: string, ci: number) => (
                                          <span key={ci} className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">{cap}</span>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* Matched Subs */}
                                  {subMatchResults[opp.id].analysis.matched_subcontractors?.length > 0 && (
                                    <div className="space-y-2 mb-3">
                                      {subMatchResults[opp.id].analysis.matched_subcontractors.map((sub: any, si: number) => (
                                        <div key={si} className={`rounded-lg p-3 border ${sub.is_small_business ? 'bg-purple-900/20 border-purple-600/30' : 'bg-gray-800 border-gray-700'}`}>
                                          <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                              <span className={`text-sm font-bold ${sub.match_score >= 80 ? 'text-green-400' : sub.match_score >= 60 ? 'text-yellow-400' : 'text-gray-400'}`}>
                                                {sub.match_score}%
                                              </span>
                                              <span className="text-sm font-medium text-white">{sub.name}</span>
                                              {sub.is_small_business && (
                                                <span className="text-xs bg-purple-600/40 text-purple-300 px-1.5 py-0.5 rounded">Small Biz</span>
                                              )}
                                              {sub.socioeconomic_certs?.length > 0 && (
                                                <span className="text-xs text-purple-400">{sub.socioeconomic_certs.join(', ')}</span>
                                              )}
                                            </div>
                                            <div className="flex items-center gap-2">
                                              {sub.email && (
                                                <a href={`mailto:${sub.email}`} onClick={(e) => e.stopPropagation()} className="text-xs text-blue-400 hover:underline">Email</a>
                                              )}
                                              {sub.phone && (
                                                <a href={`tel:${sub.phone}`} onClick={(e) => e.stopPropagation()} className="text-xs text-green-400 hover:underline">Call</a>
                                              )}
                                              {sub.website && (
                                                <a href={sub.website.startsWith('http') ? sub.website : `https://${sub.website}`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="text-xs text-cyan-400 hover:underline">Web</a>
                                              )}
                                            </div>
                                          </div>
                                          <p className="text-xs text-gray-400 mt-1">{sub.match_reason}</p>
                                          <div className="flex gap-3 mt-1 text-xs text-gray-500">
                                            {sub.role && <span>Role: <span className="text-gray-300">{sub.role}</span></span>}
                                            {sub.service_type && <span>Service: <span className="text-gray-300">{sub.service_type}</span></span>}
                                            {sub.city && sub.state && <span>Location: <span className="text-gray-300">{sub.city}, {sub.state}</span></span>}
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  )}

                                  {/* Capability Gaps */}
                                  {subMatchResults[opp.id].analysis.capability_gaps?.length > 0 && (
                                    <div className="bg-red-900/20 border border-red-600/30 rounded-lg p-3 mb-3">
                                      <div className="flex items-center justify-between mb-1">
                                        <p className="text-xs font-medium text-red-300">Capability Gaps (No matching sub in database):</p>
                                        <button
                                          onClick={async (e) => {
                                            e.stopPropagation();
                                            setMiningGapsFor(opp.id);
                                            try {
                                              showNotification('Mining Google, SAM.gov, Google Maps & Facebook for matching subs...', 'success');
                                              const resp = await api.post('/gpss/subcontractors/mine-for-gaps', {
                                                gaps: subMatchResults[opp.id].analysis.capability_gaps,
                                                suggested_searches: subMatchResults[opp.id].analysis.suggested_searches || [],
                                                location: opp.state || 'Michigan',
                                                auto_save: true
                                              });
                                              setGapMineResults(prev => ({ ...prev, [opp.id]: resp }));
                                              showNotification(`Found ${resp.total_found} subs, saved ${resp.saved_to_database} new ones to database`, 'success');
                                            } catch (err: any) {
                                              showNotification(err.message || 'Error mining for subs', 'error');
                                            } finally {
                                              setMiningGapsFor(null);
                                            }
                                          }}
                                          disabled={miningGapsFor === opp.id}
                                          className={`${miningGapsFor === opp.id ? 'bg-orange-800 cursor-wait animate-pulse' : 'bg-orange-600 hover:bg-orange-700'} text-white px-3 py-1 rounded text-xs font-semibold transition`}
                                        >
                                          {miningGapsFor === opp.id ? 'Mining All Sources...' : 'Mine for Subs'}
                                        </button>
                                      </div>
                                      <div className="flex flex-wrap gap-1">
                                        {subMatchResults[opp.id].analysis.capability_gaps.map((gap: string, gi: number) => (
                                          <span key={gi} className="text-xs bg-red-800/40 text-red-200 px-2 py-0.5 rounded">{gap}</span>
                                        ))}
                                      </div>
                                      {subMatchResults[opp.id].analysis.suggested_searches?.length > 0 && (
                                        <p className="text-xs text-red-400 mt-2">
                                          Will search: {subMatchResults[opp.id].analysis.suggested_searches.join(' | ')}
                                        </p>
                                      )}

                                      {/* Gap Mining Results */}
                                      {gapMineResults[opp.id] && (
                                        <div className="mt-3 bg-gray-800 rounded-lg p-3 border border-gray-700">
                                          <div className="flex items-center justify-between mb-2">
                                            <p className="text-xs font-medium text-green-300">
                                              Mining Results: {gapMineResults[opp.id].total_found} found, {gapMineResults[opp.id].saved_to_database} saved to database
                                            </p>
                                            <span className="text-xs text-gray-500">
                                              Sources: Google, SAM.gov, Google Maps, Facebook
                                            </span>
                                          </div>
                                          {gapMineResults[opp.id].subcontractors?.length > 0 && (
                                            <div className="space-y-1">
                                              {gapMineResults[opp.id].subcontractors.map((sub: any, si: number) => (
                                                <div key={si} className="flex items-center justify-between text-xs py-1 border-b border-gray-700/50 last:border-0">
                                                  <div className="flex items-center gap-2">
                                                    <span className="font-medium text-white">{sub.company_name}</span>
                                                    <span className="text-gray-500">{sub.service_type}</span>
                                                    {sub.certs?.length > 0 && (
                                                      <span className="bg-purple-600/30 text-purple-300 px-1.5 py-0.5 rounded text-[10px]">
                                                        {sub.certs.length} cert{sub.certs.length > 1 ? 's' : ''}
                                                      </span>
                                                    )}
                                                  </div>
                                                  <div className="flex items-center gap-2 text-gray-500">
                                                    <span>{sub.city}{sub.state ? `, ${sub.state}` : ''}</span>
                                                    <span className="text-[10px] bg-gray-700 px-1.5 py-0.5 rounded">{sub.source}</span>
                                                  </div>
                                                </div>
                                              ))}
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              )}
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>

            {/* Summary Footer */}
            <div className="mt-4 text-sm text-gray-500 text-center">
              Showing {displayedOpportunities.length} opportunities in this view • 
              {stats.filteredIneligible} ineligible filtered out
            </div>
          </div>
        )}

        {/* TAB: PROPOSALS */}
        {activeTab === 'proposals' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">Proposals & Quotes</h2>
                <p className="text-gray-400">AI-generated proposals with ProposalBio quality scoring</p>
              </div>
              <button 
                onClick={fetchProposals}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                Refresh
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Total</h3>
                <p className="text-3xl font-bold">{proposals.length}</p>
              </div>
              <div className="bg-gradient-to-br from-gray-600 to-gray-700 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Draft</h3>
                <p className="text-3xl font-bold">{proposals.filter(p => !p.status || p.status === 'Draft' || p.status === 'DRAFT').length}</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Ready</h3>
                <p className="text-3xl font-bold">{proposals.filter(p => p.status === 'Ready to Send' || p.status === 'READY TO SEND').length}</p>
              </div>
              <div className="bg-gradient-to-br from-cyan-600 to-cyan-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Sent</h3>
                <p className="text-3xl font-bold">{proposals.filter(p => p.status === 'Sent' || p.status === 'SENT' || p.status === 'Under Review').length}</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Won</h3>
                <p className="text-3xl font-bold">{proposals.filter(p => p.status === 'Accepted' || p.status === 'ACCEPTED').length}</p>
              </div>
            </div>

            {/* Proposals Table */}
            <div className="bg-gray-800 rounded-xl overflow-hidden">
              {proposals.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-700">
                      <tr>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Proposal</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Agency</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Value</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Bio Score</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Due</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {proposals.map(proposal => (
                        <tr key={proposal.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                          <td className="px-6 py-4">
                            <div className="font-bold text-blue-400">{proposal.proposalName || 'Untitled'}</div>
                            <div className="text-sm text-gray-400">{proposal.rfpNumber}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-300 text-sm">{proposal.agency || '-'}</td>
                          <td className="px-6 py-4">
                            <div className="text-green-400 font-bold">{formatCurrency(proposal.value || proposal.pricingTotal || 0)}</div>
                          </td>
                          <td className="px-6 py-4">
                            {proposal.proposalBioScore ? (
                              <div className="text-center">
                                <div className={`text-lg font-bold ${
                                  proposal.proposalBioScore >= 90 ? 'text-green-400' :
                                  proposal.proposalBioScore >= 75 ? 'text-yellow-400' :
                                  proposal.proposalBioScore >= 60 ? 'text-orange-400' :
                                  'text-red-400'
                                }`}>
                                  {Math.round(proposal.proposalBioScore)}
                                </div>
                                <div className={`text-[10px] font-semibold ${
                                  proposal.proposalBioGate === 'UNLOCKED' ? 'text-green-400' : 'text-red-400'
                                }`}>
                                  {proposal.proposalBioGate === 'UNLOCKED' ? 'READY' : 'NEEDS WORK'}
                                </div>
                              </div>
                            ) : (
                              <button
                                onClick={async () => {
                                  try {
                                    showNotification('Running ProposalBio analysis...', 'success');
                                    await api.post('/gpss/proposalbio/analyze', { proposal_id: proposal.id });
                                    fetchProposals();
                                    showNotification('ProposalBio analysis complete', 'success');
                                  } catch {
                                    showNotification('Analysis failed', 'error');
                                  }
                                }}
                                className="bg-orange-600 hover:bg-orange-700 px-2 py-1 rounded text-xs font-semibold transition"
                              >
                                Score
                              </button>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              proposal.status === 'Accepted' || proposal.status === 'ACCEPTED' ? 'bg-green-500/20 text-green-400' :
                              proposal.status === 'Sent' || proposal.status === 'SENT' || proposal.status === 'Under Review' ? 'bg-cyan-500/20 text-cyan-400' :
                              proposal.status === 'Rejected' || proposal.status === 'REJECTED' ? 'bg-red-500/20 text-red-400' :
                              proposal.status === 'Ready to Send' || proposal.status === 'READY TO SEND' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-gray-500/20 text-gray-400'
                            }`}>
                              {proposal.status || 'Draft'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-400 text-sm">{proposal.dueDate || '-'}</td>
                          <td className="px-6 py-4">
                            <div className="flex gap-2">
                              <button 
                                onClick={() => {
                                  setSelectedProposal({...proposal});
                                  setEditingSection(null);
                                  setShowProposalModal(true);
                                }}
                                className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-semibold transition"
                              >
                                Open
                              </button>
                              <button 
                                onClick={() => exportProposalPDF(proposal)}
                                className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-xs font-semibold transition"
                              >
                                Export
                              </button>
                              <button
                                onClick={async () => {
                                  if (window.confirm('Delete this proposal?')) {
                                    try {
                                      await api.delete(`/gpss/proposals/${proposal.id}`);
                                      showNotification('Proposal deleted', 'success');
                                      fetchProposals();
                                    } catch { showNotification('Delete failed', 'error'); }
                                  }
                                }}
                                className="bg-red-600/50 hover:bg-red-600 px-2 py-1 rounded text-xs font-semibold transition"
                              >
                                X
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-16">
                  <p className="text-gray-500 font-semibold mb-2 text-lg">No proposals yet</p>
                  <p className="text-sm text-gray-600 mb-6">Go to Opportunities, expand one, and click "Generate Proposal" to create your first AI proposal.</p>
                  <button 
                    onClick={() => setActiveTab('opportunities')}
                    className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                  >
                    Go to Opportunities
                  </button>
                </div>
              )}
            </div>

            {/* Workflow Guide */}
            <div className="mt-6 bg-gray-800/50 border border-gray-700 rounded-xl p-5">
              <h3 className="text-sm font-bold text-gray-400 mb-3">Proposal Workflow</h3>
              <div className="flex items-center gap-2 text-xs flex-wrap">
                <span className="bg-gray-700 text-gray-300 px-3 py-1.5 rounded-full font-semibold">Draft</span>
                <span className="text-gray-600">→</span>
                <span className="bg-yellow-700/30 text-yellow-400 px-3 py-1.5 rounded-full font-semibold">Ready to Send</span>
                <span className="text-gray-600">→</span>
                <span className="bg-cyan-700/30 text-cyan-400 px-3 py-1.5 rounded-full font-semibold">Sent</span>
                <span className="text-gray-600">→</span>
                <span className="bg-blue-700/30 text-blue-400 px-3 py-1.5 rounded-full font-semibold">Under Review</span>
                <span className="text-gray-600">→</span>
                <span className="bg-green-700/30 text-green-400 px-3 py-1.5 rounded-full font-semibold">Won</span>
                <span className="text-gray-600">/</span>
                <span className="bg-red-700/30 text-red-400 px-3 py-1.5 rounded-full font-semibold">Lost</span>
              </div>
            </div>
          </div>
        )}

        {/* TAB: SUPPLIERS */}
        {activeTab === 'suppliers' && (
          <div>
            <SuppliersTab />
          </div>
        )}

        {/* TAB: SUBCONTRACTORS */}
        {activeTab === 'subcontractors' && (
          <div>
            <SubcontractorsTab />
          </div>
        )}

        {/* TAB: CONTACTS */}
        {activeTab === 'contacts' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">👥 Contacts</h2>
                <p className="text-gray-400">Government contracting officers, program managers, and POCs</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => openContactModal()}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  ➕ Add Contact
                </button>
                <button 
                  onClick={fetchContacts}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  🔄 Refresh
                </button>
              </div>
            </div>

            {contactsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400">Loading contacts...</p>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-xl overflow-hidden">
                {contacts.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-700">
                        <tr>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Name</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Title</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Agency</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Email</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Phone</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Source</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {contacts.map(contact => (
                          <tr key={contact.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                            <td className="px-6 py-4">
                              <div className="font-bold text-blue-400">{contact.firstName} {contact.lastName}</div>
                            </td>
                            <td className="px-6 py-4 text-gray-300">{contact.title || '-'}</td>
                            <td className="px-6 py-4 text-gray-300">{contact.agency || '-'}</td>
                            <td className="px-6 py-4 text-gray-300">{contact.email || '-'}</td>
                            <td className="px-6 py-4 text-gray-300">{contact.phone || '-'}</td>
                            <td className="px-6 py-4">
                              <span className="bg-gray-600 text-gray-300 px-2 py-1 rounded text-xs">
                                {contact.source || 'Manual'}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex gap-2">
                                <button 
                                  onClick={() => openContactModal(contact)}
                                  className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm font-semibold transition"
                                >
                                  Edit
                                </button>
                                <button 
                                  onClick={() => deleteContact(contact.id)}
                                  className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm font-semibold transition"
                                >
                                  Delete
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4 opacity-20">👥</div>
                    <p className="text-gray-500 font-semibold mb-4">No contacts yet</p>
                    <p className="text-sm text-gray-600 mb-6">Add contacts manually or extract them from RFP documents</p>
                    <button 
                      onClick={() => openContactModal()}
                      className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                    >
                      ➕ Add First Contact
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: PRODUCTS */}
        {activeTab === 'products' && (() => {
          // Compute categories and filtered products
          const allCategories = Array.from(new Set(products.map(p => p.category || 'Uncategorized'))).sort();
          const filteredProducts = products.filter(p => {
            const matchesSearch = !productSearch || 
              (p.name || '').toLowerCase().includes(productSearch.toLowerCase()) ||
              (p.description || '').toLowerCase().includes(productSearch.toLowerCase()) ||
              (p.supplier || '').toLowerCase().includes(productSearch.toLowerCase());
            const matchesCat = productCategoryFilter === 'all' || (p.category || 'Uncategorized') === productCategoryFilter;
            return matchesSearch && matchesCat;
          });
          
          // Group by top-level category (before the " - ")
          const grouped: Record<string, any[]> = {};
          filteredProducts.forEach(p => {
            const cat = p.category || 'Uncategorized';
            const topCat = cat.includes(' - ') ? cat.split(' - ')[0] : cat;
            if (!grouped[topCat]) grouped[topCat] = [];
            grouped[topCat].push(p);
          });

          const withPrice = products.filter(p => p.basePrice > 0).length;

          return (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">Products Catalog</h2>
                <p className="text-gray-400">{products.length} products across {allCategories.length} categories</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => openProductModal()}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition text-sm">
                  Add Product
                </button>
                <button onClick={fetchProducts}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition text-sm">
                  Refresh
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Total Products</h3>
                <p className="text-3xl font-bold">{products.length}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Categories</h3>
                <p className="text-3xl font-bold">{Object.keys(grouped).length}</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Priced</h3>
                <p className="text-3xl font-bold">{withPrice}</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Need Pricing</h3>
                <p className="text-3xl font-bold">{products.length - withPrice}</p>
              </div>
            </div>

            {/* Search + Filter */}
            <div className="flex gap-3 mb-4">
              <input
                type="text"
                placeholder="Search products, suppliers, descriptions..."
                value={productSearch}
                onChange={e => setProductSearch(e.target.value)}
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
              <select
                value={productCategoryFilter}
                onChange={e => setProductCategoryFilter(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              >
                <option value="all">All Categories ({products.length})</option>
                {allCategories.map(cat => (
                  <option key={cat} value={cat}>{cat} ({products.filter(p => (p.category || 'Uncategorized') === cat).length})</option>
                ))}
              </select>
            </div>

            {productsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400">Loading products...</p>
              </div>
            ) : filteredProducts.length > 0 ? (
              <div className="space-y-4">
                {Object.entries(grouped).sort((a, b) => b[1].length - a[1].length).map(([topCat, items]) => (
                  <div key={topCat} className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700">
                    {/* Category Header */}
                    <div className="bg-gray-700/50 px-5 py-3 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <h3 className="font-bold text-sm text-white">{topCat}</h3>
                        <span className="text-xs bg-gray-600 text-gray-300 px-2 py-0.5 rounded-full">{items.length} items</span>
                      </div>
                      <div className="text-xs text-gray-400">
                        {items.filter(i => i.basePrice > 0).length > 0 && (
                          <span className="text-green-400">{items.filter(i => i.basePrice > 0).length} priced</span>
                        )}
                      </div>
                    </div>
                    {/* Products Table */}
                    <table className="w-full">
                      <thead>
                        <tr className="text-xs text-gray-500 border-b border-gray-700">
                          <th className="text-left px-5 py-2 font-medium">Product</th>
                          <th className="text-left px-5 py-2 font-medium">Sub-Category</th>
                          <th className="text-left px-5 py-2 font-medium">Supplier</th>
                          <th className="text-right px-5 py-2 font-medium">Price</th>
                          <th className="text-right px-5 py-2 font-medium w-24">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map(product => (
                          <React.Fragment key={product.id}>
                            <tr 
                              className="border-t border-gray-700/50 hover:bg-gray-700/30 cursor-pointer"
                              onClick={() => setExpandedProductId(expandedProductId === product.id ? null : product.id)}
                            >
                              <td className="px-5 py-2.5">
                                <div className="text-sm font-medium text-gray-200">{product.name}</div>
                              </td>
                              <td className="px-5 py-2.5 text-xs text-gray-400">
                                {(product.category || '').includes(' - ') ? product.category.split(' - ').slice(1).join(' - ') : ''}
                              </td>
                              <td className="px-5 py-2.5 text-xs text-gray-400">{product.supplier || '-'}</td>
                              <td className="px-5 py-2.5 text-right">
                                {product.basePrice > 0 ? (
                                  <div>
                                    <span className="text-green-400 font-semibold text-sm">${product.basePrice.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                                    <span className="text-gray-500 text-[10px] ml-1">/{product.unit || 'ea'}</span>
                                  </div>
                                ) : (
                                  <span className="text-gray-600 text-xs">-</span>
                                )}
                              </td>
                              <td className="px-5 py-2.5 text-right">
                                <div className="flex gap-1 justify-end">
                                  <button onClick={(e) => { e.stopPropagation(); openProductModal(product); }}
                                    className="bg-gray-600 hover:bg-gray-500 px-2 py-1 rounded text-[10px] font-semibold transition">Edit</button>
                                  <button onClick={(e) => { e.stopPropagation(); deleteProduct(product.id); }}
                                    className="bg-red-600/40 hover:bg-red-600 px-2 py-1 rounded text-[10px] font-semibold transition">X</button>
                                </div>
                              </td>
                            </tr>
                            {expandedProductId === product.id && (
                              <tr className="border-t border-gray-700/30">
                                <td colSpan={5} className="px-5 py-3 bg-gray-750/30">
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                                    <div>
                                      <p className="text-gray-500 font-medium mb-1">Description / Notes</p>
                                      <p className="text-gray-300 whitespace-pre-wrap">{product.description || 'No description'}</p>
                                    </div>
                                    <div className="space-y-2">
                                      {product.rawPrice && <div><span className="text-gray-500">Original Pricing:</span> <span className="text-green-400 ml-1 font-mono">{product.rawPrice}</span></div>}
                                      {product.basePrice > 0 && <div><span className="text-gray-500">Parsed Unit Price:</span> <span className="text-green-400 ml-1">${product.basePrice.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/{product.unit || 'ea'}</span></div>}
                                      {product.manufacturers && <div><span className="text-gray-500">Manufacturer:</span> <span className="text-gray-300 ml-1">{product.manufacturers}</span></div>}
                                      {product.supplier && <div><span className="text-gray-500">Supplier:</span> <span className="text-gray-300 ml-1">{product.supplier}</span></div>}
                                      {product.created && <div><span className="text-gray-500">Added:</span> <span className="text-gray-300 ml-1">{product.created}</span></div>}
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 bg-gray-800 rounded-xl">
                <p className="text-gray-500 font-semibold mb-2">
                  {products.length === 0 ? 'No products yet' : 'No products match your search'}
                </p>
                {products.length === 0 ? (
                  <>
                    <p className="text-sm text-gray-600 mb-6">Add products from bid documents and supplier quotes</p>
                    <button onClick={() => openProductModal()}
                      className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition">
                      Add First Product
                    </button>
                  </>
                ) : (
                  <button onClick={() => { setProductSearch(''); setProductCategoryFilter('all'); }}
                    className="text-blue-400 hover:underline text-sm mt-2">Clear filters</button>
                )}
              </div>
            )}
          </div>
          );
        })()}

        {/* TAB: ANALYTICS */}
        {activeTab === 'pricing' && (
          <PricingDashboard />
        )}

        {activeTab === 'proposalbio' && (
          <ProposalBioAnalyzer />
        )}

        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📈 Analytics & Insights</h2>
              <p className="text-gray-400">Performance metrics and trends</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Pipeline (Active Bids)</h3>
                <p className="text-4xl font-bold mb-1">{stats.pipelineCount}</p>
                <p className="text-sm text-white/70">Your Pursuits</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">EDWOSB Set-Asides</h3>
                <p className="text-4xl font-bold mb-1">{stats.edwsbSetAsides}</p>
                <p className="text-sm text-white/70">Exclusive</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Proposals Sent</h3>
                <p className="text-4xl font-bold mb-1">{proposals.length}</p>
                <p className="text-sm text-white/70">All Time</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Win Rate</h3>
                <p className="text-4xl font-bold mb-1">
                  {proposals.filter(p => p.status === 'Sent' || p.status === 'Under Review' || p.status === 'Accepted' || p.status === 'Rejected').length > 0 
                    ? Math.round((proposals.filter(p => p.status === 'Accepted').length / proposals.filter(p => p.status === 'Accepted' || p.status === 'Rejected').length) * 100) 
                    : 0}%
                </p>
                <p className="text-sm text-white/70">Won / (Won + Lost)</p>
              </div>
            </div>

            {/* Opportunity Categories */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Opportunity Categories</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-blue-900/30 border border-blue-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2">{stats.pipelineCount}</div>
                  <div className="text-sm font-semibold text-blue-400">Active Pipeline</div>
                </div>
                <div className="bg-green-900/30 border border-green-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2">{stats.edwsbSetAsides}</div>
                  <div className="text-sm font-semibold text-green-400">EDWOSB / WOSB</div>
                </div>
                <div className="bg-purple-900/30 border border-purple-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2">{stats.homeStateOpps}</div>
                  <div className="text-sm font-semibold text-purple-400">Michigan (Home State)</div>
                </div>
                <div className="bg-yellow-900/30 border border-yellow-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2">{stats.forecastsCount}</div>
                  <div className="text-sm font-semibold text-yellow-400">Forecasts</div>
                </div>
              </div>
            </div>

            {/* Filtering Stats */}
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">System Filtering</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-green-900/30 border border-green-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-green-400">{stats.totalEligible}</div>
                  <div className="text-sm text-gray-300">Total Eligible Opportunities</div>
                </div>
                <div className="bg-red-900/30 border border-red-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-red-400">{stats.filteredIneligible}</div>
                  <div className="text-sm text-gray-300">Filtered Out (Ineligible Set-Asides)</div>
                </div>
                <div className="bg-blue-900/30 border border-blue-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-blue-400">
                    {stats.totalEligible > 0 ? Math.round((stats.edwsbSetAsides / stats.totalEligible) * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-300">EDWOSB % of Eligible</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
          <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 sticky top-0 z-10">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">{selectedContact ? 'Edit Contact' : 'Add Contact'}</h2>
                <button 
                  onClick={() => {
                    setShowContactModal(false);
                    resetContactForm();
                  }}
                  className="text-white hover:text-gray-300 text-3xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">First Name *</label>
                  <input 
                    type="text"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={contactFormData.firstName}
                    onChange={(e) => setContactFormData({...contactFormData, firstName: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Last Name *</label>
                  <input 
                    type="text"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={contactFormData.lastName}
                    onChange={(e) => setContactFormData({...contactFormData, lastName: e.target.value})}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Email</label>
                <input 
                  type="email"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={contactFormData.email}
                  onChange={(e) => setContactFormData({...contactFormData, email: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Phone</label>
                <input 
                  type="tel"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={contactFormData.phone}
                  onChange={(e) => setContactFormData({...contactFormData, phone: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Title</label>
                <input 
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={contactFormData.title}
                  onChange={(e) => setContactFormData({...contactFormData, title: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Agency</label>
                <input 
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={contactFormData.agency}
                  onChange={(e) => setContactFormData({...contactFormData, agency: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Department</label>
                <input 
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={contactFormData.department}
                  onChange={(e) => setContactFormData({...contactFormData, department: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">State</label>
                  <input 
                    type="text"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={contactFormData.state}
                    onChange={(e) => setContactFormData({...contactFormData, state: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Source</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={contactFormData.source}
                    onChange={(e) => setContactFormData({...contactFormData, source: e.target.value})}
                  >
                    <option value="Manual">Manual</option>
                    <option value="RFP Extraction">RFP Extraction</option>
                    <option value="SAM.gov">SAM.gov</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 pt-4">
                <button 
                  onClick={() => selectedContact ? updateContact(selectedContact.id) : createContact()}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {selectedContact ? 'Update' : 'Create'}
                </button>
                <button 
                  onClick={() => {
                    setShowContactModal(false);
                    resetContactForm();
                  }}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Product Modal */}
      {showProductModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
          <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 sticky top-0 z-10">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">{selectedProduct ? 'Edit Product' : 'Add Product'}</h2>
                <button 
                  onClick={() => {
                    setShowProductModal(false);
                    resetProductForm();
                  }}
                  className="text-white hover:text-gray-300 text-3xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Product Name *</label>
                <input 
                  type="text"
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  value={productFormData.name}
                  onChange={(e) => setProductFormData({...productFormData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Description</label>
                <textarea 
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  rows={3}
                  value={productFormData.description}
                  onChange={(e) => setProductFormData({...productFormData, description: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Category</label>
                  <input 
                    type="text"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={productFormData.category}
                    onChange={(e) => setProductFormData({...productFormData, category: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Service Category</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={productFormData.serviceCategory}
                    onChange={(e) => setProductFormData({...productFormData, serviceCategory: e.target.value})}
                  >
                    <option value="">Select...</option>
                    <option value="NEMT">NEMT</option>
                    <option value="Medical Transport">Medical Transport</option>
                    <option value="Healthcare IT">Healthcare IT</option>
                    <option value="Consulting">Consulting</option>
                    <option value="Staffing">Staffing</option>
                    <option value="Facilities">Facilities</option>
                    <option value="Professional Services">Professional Services</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Base Price *</label>
                  <input 
                    type="number"
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={productFormData.basePrice}
                    onChange={(e) => setProductFormData({...productFormData, basePrice: parseFloat(e.target.value) || 0})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Unit</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={productFormData.unit}
                    onChange={(e) => setProductFormData({...productFormData, unit: e.target.value})}
                  >
                    <option value="each">Each</option>
                    <option value="hour">Hour</option>
                    <option value="day">Day</option>
                    <option value="month">Month</option>
                    <option value="year">Year</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 pt-4">
                <button 
                  onClick={() => selectedProduct ? updateProduct(selectedProduct.id) : createProduct()}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {selectedProduct ? 'Update' : 'Create'}
                </button>
                <button 
                  onClick={() => {
                    setShowProductModal(false);
                    resetProductForm();
                  }}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Proposal Viewer/Editor Modal */}
      {showProposalModal && selectedProposal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-gray-800 rounded-xl max-w-5xl w-full max-h-[95vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-5 sticky top-0 z-10">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold mb-1">{selectedProposal.proposalName || 'Untitled Proposal'}</h2>
                  <div className="flex gap-3 text-sm text-white/80">
                    <span>RFP: {selectedProposal.rfpNumber || '-'}</span>
                    <span>|</span>
                    <span>${(selectedProposal.value || selectedProposal.pricingTotal || 0).toLocaleString()}</span>
                    <span>|</span>
                    <span>Due: {selectedProposal.dueDate || '-'}</span>
                  </div>
                </div>
                <button onClick={() => { setShowProposalModal(false); setEditingSection(null); }} className="text-white/70 hover:text-white text-2xl">x</button>
              </div>

              {/* Status Workflow Bar */}
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-xs text-white/60 mr-1">Status:</span>
                {['DRAFT', 'READY TO SEND', 'SENT', 'UNDER REVIEW', 'ACCEPTED', 'REJECTED'].map(status => {
                  const currentStatus = (selectedProposal.status || 'Draft').toUpperCase();
                  const isActive = currentStatus === status;
                  const colorMap: Record<string, string> = {
                    'DRAFT': 'bg-gray-600',
                    'READY TO SEND': 'bg-yellow-600',
                    'SENT': 'bg-cyan-600',
                    'UNDER REVIEW': 'bg-blue-600',
                    'ACCEPTED': 'bg-green-600',
                    'REJECTED': 'bg-red-600',
                  };
                  return (
                    <button
                      key={status}
                      onClick={async () => {
                        setUpdatingStatus(true);
                        try {
                          const updateData: any = { status };
                          if (status === 'SENT') updateData.sentDate = new Date().toISOString();
                          await api.put(`/gpss/proposals/${selectedProposal.id}`, updateData);
                          setSelectedProposal({...selectedProposal, status: status as any, sentDate: status === 'SENT' ? new Date().toISOString() : selectedProposal.sentDate});
                          showNotification(`Status updated to ${status}`, 'success');
                          fetchProposals();
                        } catch { showNotification('Status update failed', 'error'); }
                        finally { setUpdatingStatus(false); }
                      }}
                      disabled={updatingStatus}
                      className={`px-2 py-1 rounded text-[10px] font-bold transition ${
                        isActive ? `${colorMap[status]} text-white ring-2 ring-white/50` : 'bg-white/10 text-white/50 hover:bg-white/20 hover:text-white'
                      }`}
                    >
                      {status === 'ACCEPTED' ? 'WON' : status === 'REJECTED' ? 'LOST' : status}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Modal Content - Editable Sections */}
            <div className="p-5 space-y-4">
              {/* Editable Section Helper */}
              {[
                { key: 'executiveSummary', label: 'Executive Summary', color: 'blue' },
                { key: 'technicalApproach', label: 'Technical Approach', color: 'green' },
                { key: 'staffingPlan', label: 'Staffing Plan', color: 'purple' },
                { key: 'pastPerformance', label: 'Past Performance', color: 'yellow' },
              ].map(section => (
                <div key={section.key} className="bg-gray-700 p-4 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`text-sm font-bold text-${section.color}-400`}>{section.label}</h3>
                    {editingSection === section.key ? (
                      <div className="flex gap-2">
                        <button
                          onClick={async () => {
                            try {
                              await api.put(`/gpss/proposals/${selectedProposal.id}`, { [section.key]: editBuffer });
                              setSelectedProposal({...selectedProposal, [section.key]: editBuffer} as any);
                              setEditingSection(null);
                              showNotification(`${section.label} updated`, 'success');
                            } catch { showNotification('Save failed', 'error'); }
                          }}
                          className="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-[10px] font-bold transition"
                        >Save</button>
                        <button
                          onClick={() => setEditingSection(null)}
                          className="bg-gray-600 hover:bg-gray-500 px-2 py-1 rounded text-[10px] font-bold transition"
                        >Cancel</button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setEditingSection(section.key);
                          setEditBuffer((selectedProposal as any)[section.key] || '');
                        }}
                        className="bg-gray-600 hover:bg-gray-500 px-2 py-1 rounded text-[10px] font-bold transition"
                      >Edit</button>
                    )}
                  </div>
                  {editingSection === section.key ? (
                    <textarea
                      value={editBuffer}
                      onChange={e => setEditBuffer(e.target.value)}
                      className="w-full bg-gray-800 text-gray-200 text-sm rounded-lg p-3 border border-gray-600 focus:border-blue-500 focus:outline-none min-h-[120px]"
                      autoFocus
                    />
                  ) : (
                    <p className="text-gray-300 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto">
                      {(selectedProposal as any)[section.key] || <span className="text-gray-500 italic">No content yet. Click Edit to add.</span>}
                    </p>
                  )}
                </div>
              ))}

              {/* Pricing Section */}
              <div className="bg-gradient-to-br from-green-900/20 to-green-700/20 border border-green-700/50 p-4 rounded-xl">
                <h3 className="text-sm font-bold text-green-400 mb-2">Pricing</h3>
                <div className="text-3xl font-black text-green-400 mb-3">
                  ${(selectedProposal.pricingTotal || 0).toLocaleString()}
                </div>
                
                {selectedProposal.pricingBreakdown && (selectedProposal.pricingBreakdown as any).labor !== undefined && (
                  <div className="mb-3 bg-gray-800/50 p-3 rounded-lg">
                    <div className="grid grid-cols-2 gap-1.5 text-sm">
                      <div className="text-gray-400">Labor:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).labor || 0).toLocaleString()}</div>
                      <div className="text-gray-400">Materials:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).materials || 0).toLocaleString()}</div>
                      <div className="text-gray-400">Other:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).other || 0).toLocaleString()}</div>
                      <div className="text-green-400 font-bold pt-1 border-t border-gray-600">Total Bid:</div>
                      <div className="text-green-400 font-bold pt-1 border-t border-gray-600">${(selectedProposal.pricingTotal || 0).toLocaleString()}</div>
                    </div>
                  </div>
                )}
                
                {selectedProposal.pricingJustification && (
                  <p className="text-gray-400 text-xs whitespace-pre-wrap">{selectedProposal.pricingJustification}</p>
                )}
              </div>

              {/* Compliance Checklist */}
              {selectedProposal.complianceChecklist && Object.keys(selectedProposal.complianceChecklist).length > 0 && (
                <div className="bg-gray-700 p-4 rounded-xl">
                  <h3 className="text-sm font-bold text-blue-400 mb-2">Compliance</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedProposal.complianceChecklist).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2 text-sm">
                        <span className={value ? 'text-green-400' : 'text-red-400'}>{value ? '✓' : '✗'}</span>
                        <span className="text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ProposalBio Score */}
              {selectedProposal.proposalBioScore && (
                <div className={`p-4 rounded-xl border ${selectedProposal.proposalBioGate === 'UNLOCKED' ? 'bg-green-900/20 border-green-600/40' : 'bg-red-900/20 border-red-600/40'}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-gray-300">ProposalBio Score</h3>
                      <span className={`text-3xl font-black ${
                        selectedProposal.proposalBioScore >= 90 ? 'text-green-400' :
                        selectedProposal.proposalBioScore >= 75 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>{Math.round(selectedProposal.proposalBioScore)}</span>
                      <span className="text-gray-500 text-sm ml-1">/100</span>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                      selectedProposal.proposalBioGate === 'UNLOCKED' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                    }`}>
                      {selectedProposal.proposalBioGate === 'UNLOCKED' ? 'READY TO SUBMIT' : 'NEEDS IMPROVEMENT'}
                    </div>
                  </div>
                  {selectedProposal.proposalBioCriticalIssues && selectedProposal.proposalBioCriticalIssues.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-red-400 font-semibold mb-1">Issues to fix:</p>
                      {selectedProposal.proposalBioCriticalIssues.map((issue: any, i: number) => (
                        <p key={i} className="text-xs text-red-300 ml-2">- {typeof issue === 'string' ? issue : issue.description || JSON.stringify(issue)}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-gray-700/80 p-4 flex gap-3 justify-between sticky bottom-0 border-t border-gray-600">
              <div className="flex gap-2">
                <button 
                  onClick={() => {
                    setComplianceRfpContent(selectedProposal.executiveSummary + '\n' + selectedProposal.technicalApproach);
                    setShowComplianceChecker(true);
                  }}
                  className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  Compliance Check
                </button>
                <button
                  onClick={async () => {
                    try {
                      showNotification('Running ProposalBio analysis...', 'success');
                      await api.post('/gpss/proposalbio/analyze', { proposal_id: selectedProposal.id });
                      fetchProposals();
                      showNotification('ProposalBio analysis complete', 'success');
                    } catch { showNotification('Analysis failed', 'error'); }
                  }}
                  className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  Run ProposalBio
                </button>
              </div>
              <div className="flex gap-2">
                <button onClick={() => { setShowProposalModal(false); setEditingSection(null); }}
                  className="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg text-sm font-semibold transition">Close</button>
                <button onClick={() => saveProposal(selectedProposal)}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-semibold transition">Save</button>
                <button onClick={() => exportProposalPDF(selectedProposal)}
                  className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm font-semibold transition">Export</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pricing Calculator Modal */}
      {showPricingCalculator && pricingOpportunity && (
        <PricingCalculator
          opportunityId={pricingOpportunity.id}
          opportunityTitle={pricingOpportunity.title}
          estimatedValue={pricingOpportunity.value}
          onClose={() => {
            setShowPricingCalculator(false);
            setPricingOpportunity(null);
          }}
          onSelectPrice={(price, strategy) => {
            showNotification(`✅ Selected ${strategy} pricing: $${price.toLocaleString()}`, 'success');
            setShowPricingCalculator(false);
            setPricingOpportunity(null);
          }}
        />
      )}

      {/* Compliance Checker Modal */}
      {showComplianceChecker && selectedProposal && (
        <ComplianceChecker
          rfpContent={complianceRfpContent}
          proposalData={selectedProposal}
          onClose={() => setShowComplianceChecker(false)}
        />
      )}

      {/* Notification Toast */}
      {notification && (
        <div className={`fixed top-6 right-6 border px-6 py-4 rounded-lg shadow-2xl max-w-md z-50 ${
          notification.type === 'success' 
            ? 'bg-gray-800 border-green-500' 
            : 'bg-gray-800 border-red-500'
        }`}>
          <p className={`font-semibold ${
            notification.type === 'success' ? 'text-green-400' : 'text-red-400'
          }`}>
            {notification.message}
          </p>
        </div>
      )}
    </div>
  );
};

export default GPSSSystem;

