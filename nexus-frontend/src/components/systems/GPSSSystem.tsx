import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import PricingCalculator from '../PricingCalculator';
import ComplianceChecker from '../ComplianceChecker';

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
  status: 'Draft' | 'Review' | 'Ready to Send' | 'Sent' | 'Under Review' | 'Accepted' | 'Rejected';
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
}

const GPSSSystem: React.FC<GPSSSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  // Opportunities State
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    source: 'all',
    state: 'all',
    edwsbOnly: false,
    urgency: 'all',
    homeStatesOnly: false
  });

  // Proposals State
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [proposalsLoading, setProposalsLoading] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [generatingProposal, setGeneratingProposal] = useState(false);

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
    { id: 'proposals', label: '📝 Proposals' },
    { id: 'contacts', label: '👥 Contacts' },
    { id: 'products', label: '📦 Products' },
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
      // Fetch from Airtable via backend
      const response = await api.getGpssOpportunities();
      
      if (response.opportunities && response.opportunities.length > 0) {
        setOpportunities(response.opportunities);
      } else {
        // Use mock data if no opportunities in Airtable yet
        setOpportunities(getMockOpportunities());
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      // Fallback to mock data
      setOpportunities(getMockOpportunities());
    } finally {
      setLoading(false);
    }
  };

  const getMockOpportunities = (): Opportunity[] => [
    {
      id: '1',
      title: 'NEMT Services - Medicare Advantage',
      rfpNumber: 'HHS-CMS-2026-0045',
      agency: 'Centers for Medicare & Medicaid Services',
      value: 25000000,
      dueDate: '2026-02-15',
      source: 'Federal',
      sourcePortal: 'SAM.gov',
      state: 'Federal',
      setAsideType: 'EDWOSB',
      edwsbEligible: true,
      priorityScore: 95,
      urgency: 'Critical',
      category: 'NEMT',
      homeStatePriority: false,
      internalStatus: 'New'
    },
    {
      id: '2',
      title: 'Emergency Medical Transportation - Statewide',
      rfpNumber: 'MI-MDHHS-2026-0123',
      agency: 'Michigan Department of Health & Human Services',
      value: 18000000,
      dueDate: '2026-03-01',
      source: 'State',
      sourcePortal: 'SIGMA VSS',
      state: 'MI',
      setAsideType: 'WOSB',
      edwsbEligible: true,
      priorityScore: 92,
      urgency: 'High',
      category: 'NEMT',
      homeStatePriority: true,
      internalStatus: 'Reviewing'
    },
    {
      id: '3',
      title: 'Disaster Response Supply Pre-Positioning',
      rfpNumber: 'FEMA-R4-2026-0089',
      agency: 'FEMA Region 4 (Southeast)',
      value: 12000000,
      dueDate: '2026-02-28',
      source: 'Federal',
      sourcePortal: 'SAM.gov',
      state: 'Multi-State',
      setAsideType: 'Small Business',
      edwsbEligible: false,
      priorityScore: 88,
      urgency: 'High',
      category: 'Emergency Supplies',
      homeStatePriority: true,
      internalStatus: 'New'
    },
    {
      id: '4',
      title: 'School Transportation Services',
      rfpNumber: 'GA-DOE-2026-0156',
      agency: 'Georgia Department of Education',
      value: 8500000,
      dueDate: '2026-04-15',
      source: 'State',
      sourcePortal: 'Georgia Procurement Registry',
      state: 'GA',
      setAsideType: 'Unrestricted',
      edwsbEligible: false,
      priorityScore: 75,
      urgency: 'Medium',
      category: 'Transportation Services',
      homeStatePriority: true,
      internalStatus: 'New'
    },
    {
      id: '5',
      title: 'Emergency Generator Supply & Installation',
      rfpNumber: 'CP-2026-0234',
      agency: 'Choice Partners Cooperative',
      value: 15000000,
      dueDate: '2026-03-20',
      source: 'Cooperative',
      sourcePortal: 'Choice Partners',
      state: 'Multi-State',
      setAsideType: 'Unrestricted',
      edwsbEligible: false,
      priorityScore: 82,
      urgency: 'Medium',
      category: 'Emergency Supplies',
      homeStatePriority: false,
      internalStatus: 'New'
    },
    {
      id: '6',
      title: 'Non-Emergency Medical Transport - Medicaid',
      rfpNumber: 'TX-HHS-2026-0467',
      agency: 'Texas Health & Human Services',
      value: 22000000,
      dueDate: '2026-02-22',
      source: 'State',
      sourcePortal: 'ESBD',
      state: 'TX',
      setAsideType: 'HUB',
      edwsbEligible: true,
      priorityScore: 90,
      urgency: 'Critical',
      category: 'NEMT',
      homeStatePriority: true,
      internalStatus: 'Bidding'
    }
  ];

  // Filter opportunities based on selected filters
  const filteredOpportunities = opportunities.filter(opp => {
    if (filters.source !== 'all' && opp.source !== filters.source) return false;
    if (filters.state !== 'all' && opp.state !== filters.state) return false;
    if (filters.edwsbOnly && !opp.edwsbEligible) return false;
    if (filters.urgency !== 'all' && opp.urgency !== filters.urgency) return false;
    if (filters.homeStatesOnly && !opp.homeStatePriority) return false;
    return true;
  });

  // Calculate stats
  const stats = {
    federalOpps: opportunities.filter(o => o.source === 'Federal').length,
    edwsbSetAsides: opportunities.filter(o => o.edwsbEligible).length,
    homeStateOpps: opportunities.filter(o => o.homeStatePriority).length,
    criticalUrgency: opportunities.filter(o => o.urgency === 'Critical').length,
    totalPipeline: opportunities.reduce((sum, o) => sum + o.value, 0),
    totalOpportunities: opportunities.length
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value}`;
  };

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
      const proposalResult = await api.saveGpssProposal(proposal);
      
      // Also save pricing data to Pricing History (for learning)
      try {
        // We'll create this endpoint to auto-save pricing history
        // This helps the AI learn from every proposal we generate
        const pricingHistory = {
          opportunityId: proposal.opportunityId,
          proposalId: proposalResult.proposalId,
          totalBid: proposal.pricingTotal,
          estimatedCosts: (proposal.pricingBreakdown as any)?.total_cost || 0,
          agency: proposal.agency,
          rfpNumber: proposal.rfpNumber,
          status: 'Pending', // Will update when we win/lose
          notes: 'Auto-saved from proposal generation'
        };
        
        // This will be a background save - don't block on it
        // api.savePricingHistory(pricingHistory).catch(err => console.log('Pricing history save failed:', err));
      } catch (err) {
        // Silent fail - pricing history is nice to have but not critical
        console.log('Could not save pricing history:', err);
      }
      
      showNotification('✅ Proposal saved to Airtable!', 'success');
      setShowProposalModal(false);
      fetchProposals();
    } catch (error) {
      showNotification('❌ Error saving proposal', 'error');
    }
  };

  const exportProposalPDF = (proposal: Proposal) => {
    // Create a simple text version for now
    const content = `
PROPOSAL FOR: ${proposal.proposalName}

RFP Number: ${proposal.rfpNumber}
Agency: ${proposal.agency}
Value: $${proposal.value.toLocaleString()}
Due Date: ${proposal.dueDate}

EXECUTIVE SUMMARY
${proposal.executiveSummary}

TECHNICAL APPROACH
${proposal.technicalApproach}

STAFFING PLAN
${proposal.staffingPlan}

PAST PERFORMANCE
${proposal.pastPerformance}

PRICING
Total: $${proposal.pricingTotal.toLocaleString()}
${proposal.pricingJustification}

Generated by NEXUS GPSS System
${new Date().toLocaleDateString()}
    `;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${proposal.rfpNumber}_Proposal.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    showNotification('📄 Proposal exported!', 'success');
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

  // PDF extraction now handled by backend - function removed for clean code

  const extractContacts = async () => {
    if (!selectedFile) return;

    setIsExtracting(true);

    try {
      // Create FormData to upload the actual PDF file
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://127.0.0.1:8000/extract-contacts', {
        method: 'POST',
        body: formData  // Send the actual file, not JSON
      });

      const result = await response.json();

      if (result.success) {
        showNotification(`🎉 Found ${result.contacts_found} contacts! Stored ${result.contacts_stored} in Airtable.`, 'success');
        setSelectedFile(null);
        const fileInput = document.getElementById('fileInput') as HTMLInputElement;
        if (fileInput) fileInput.value = '';

        setTimeout(() => setActiveTab('contacts'), 2000);
      } else {
        const errorMsg = result.error || 'No contacts found in document';
        showNotification(`❌ ${errorMsg}`, 'error');
      }
    } catch (error) {
      console.error('Contact extraction error:', error);
      showNotification('❌ Error extracting contacts from PDF', 'error');
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
              <h2 className="text-3xl font-bold mb-2">Government Contracting Command Center</h2>
              <p className="text-gray-400">Nationwide Federal + 6-State Operation • EDWOSB Certified</p>
            </div>

            {/* Enhanced Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-xl">
                <div className="text-3xl mb-2">🦅</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">Federal Opportunities</h3>
                <p className="text-4xl font-bold mb-1">{stats.federalOpps}</p>
                <p className="text-sm text-white/70">SAM.gov + Agencies</p>
              </div>

              <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                <div className="text-3xl mb-2">⭐</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">EDWOSB Set-Asides</h3>
                <p className="text-4xl font-bold mb-1">{stats.edwsbSetAsides}</p>
                <p className="text-sm text-white/70">Exclusive Access</p>
              </div>

              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-6 rounded-xl">
                <div className="text-3xl mb-2">🏠</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">Home State Opps</h3>
                <p className="text-4xl font-bold mb-1">{stats.homeStateOpps}</p>
                <p className="text-sm text-white/70">MI, GA, MD, TX, CA, IL</p>
              </div>

              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-6 rounded-xl">
                <div className="text-3xl mb-2">💰</div>
                <h3 className="text-sm font-semibold text-white/80 mb-2">Pipeline Value</h3>
                <p className="text-4xl font-bold mb-1">{formatCurrency(stats.totalPipeline)}</p>
                <p className="text-sm text-white/70">{stats.totalOpportunities} Active RFPs</p>
              </div>
            </div>

            {/* Critical Alerts */}
            {stats.criticalUrgency > 0 && (
              <div className="mb-6 bg-red-900/20 border border-red-500/50 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">🚨</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-red-400 text-lg">Critical Deadline Alert</h3>
                    <p className="text-sm text-gray-300">{stats.criticalUrgency} opportunities due within 7 days</p>
                  </div>
                  <button
                    onClick={() => {
                      setFilters({ ...filters, urgency: 'Critical' });
                      setActiveTab('opportunities');
                    }}
                    className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold transition"
                  >
                    View Now →
                  </button>
                </div>
              </div>
            )}

            {/* Recent Activity Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recent Opportunities */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">🎯 High Priority Opportunities</h3>
                <div className="space-y-3">
                  {opportunities
                    .filter(o => o.priorityScore >= 85)
                    .slice(0, 3)
                    .map(opp => (
                      <div key={opp.id} className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg hover:bg-gray-700 transition cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {opp.edwsbEligible && <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/30 font-bold">EDWOSB</span>}
                              {opp.homeStatePriority && <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30 font-bold">HOME STATE</span>}
                            </div>
                            <h4 className="font-bold text-blue-400">{opp.title}</h4>
                            <p className="text-sm text-gray-400">{opp.agency}</p>
                          </div>
                          <span className={`text-xs font-bold px-2 py-1 rounded border ${getUrgencyColor(opp.urgency)}`}>
                            {opp.urgency}
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-400">{opp.rfpNumber}</span>
                          <span className="text-green-400 font-bold">{formatCurrency(opp.value)}</span>
                        </div>
                        <div className="mt-2 flex justify-between items-center text-xs">
                          <span className="text-gray-500">Due: {opp.dueDate}</span>
                          <span className="text-purple-400 font-semibold">Score: {opp.priorityScore}/100</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Source Breakdown */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">📊 Opportunity Sources</h3>
                <div className="space-y-4">
                  <div className="bg-blue-900/30 border border-blue-700/50 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-blue-400">Federal (SAM.gov)</span>
                      <span className="text-2xl font-bold">{opportunities.filter(o => o.source === 'Federal').length}</span>
                    </div>
                    <div className="text-xs text-gray-400">HHS, FEMA, DOD, VA</div>
                  </div>

                  <div className="bg-purple-900/30 border border-purple-700/50 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-purple-400">State Portals</span>
                      <span className="text-2xl font-bold">{opportunities.filter(o => o.source === 'State').length}</span>
                    </div>
                    <div className="text-xs text-gray-400">MI, GA, MD, TX, CA, IL</div>
                  </div>

                  <div className="bg-green-900/30 border border-green-700/50 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-green-400">Cooperative Purchasing</span>
                      <span className="text-2xl font-bold">{opportunities.filter(o => o.source === 'Cooperative').length}</span>
                    </div>
                    <div className="text-xs text-gray-400">Choice Partners, Sourcewell, NASPO</div>
                  </div>

                  <div className="bg-orange-900/30 border border-orange-700/50 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-orange-400">Local Governments</span>
                      <span className="text-2xl font-bold">{opportunities.filter(o => o.source === 'Local').length}</span>
                    </div>
                    <div className="text-xs text-gray-400">Counties, Cities, Transit</div>
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

        {/* TAB: OPPORTUNITY DISCOVERY (NEW!) */}
        {activeTab === 'discovery' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🔍 Opportunity Discovery Engine</h2>
              <p className="text-gray-400">Real-time monitoring of federal, state, and cooperative portals</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Federal Feed */}
              <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700/50 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="text-3xl">🦅</div>
                  <div>
                    <h3 className="font-bold text-xl text-blue-400">Federal</h3>
                    <p className="text-xs text-gray-400">SAM.gov • GSA • Agencies</p>
                  </div>
                </div>
                <div className="text-4xl font-black mb-2">{stats.federalOpps}</div>
                <div className="text-sm text-gray-400 mb-4">Active Opportunities</div>
                <button className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition">
                  Browse Federal →
                </button>
              </div>

              {/* Home States Feed */}
              <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/50 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="text-3xl">🏠</div>
                  <div>
                    <h3 className="font-bold text-xl text-purple-400">Home States</h3>
                    <p className="text-xs text-gray-400">MI • GA • MD • TX • CA • IL</p>
                  </div>
                </div>
                <div className="text-4xl font-black mb-2">{stats.homeStateOpps}</div>
                <div className="text-sm text-gray-400 mb-4">Priority Opportunities</div>
                <button 
                  onClick={() => {
                    setFilters({ ...filters, homeStatesOnly: true });
                    setActiveTab('opportunities');
                  }}
                  className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  Browse States →
                </button>
              </div>

              {/* EDWOSB Set-Asides */}
              <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700/50 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="text-3xl">⭐</div>
                  <div>
                    <h3 className="font-bold text-xl text-green-400">EDWOSB Only</h3>
                    <p className="text-xs text-gray-400">Exclusive Set-Asides</p>
                  </div>
                </div>
                <div className="text-4xl font-black mb-2">{stats.edwsbSetAsides}</div>
                <div className="text-sm text-gray-400 mb-4">Eligible Opportunities</div>
                <button 
                  onClick={() => {
                    setFilters({ ...filters, edwsbOnly: true });
                    setActiveTab('opportunities');
                  }}
                  className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  Browse EDWOSB →
                </button>
              </div>
            </div>

            {/* Mining Control Panel */}
            <div className="bg-gradient-to-br from-green-900/30 to-emerald-800/20 border border-green-700/50 rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-green-400 mb-1">🚀 Opportunity Discovery</h3>
                  <p className="text-sm text-gray-400">Scan portals and RSS feeds for new opportunities</p>
                </div>
                <div className="flex gap-3 flex-wrap">
                  <button 
                    onClick={async () => {
                      try {
                        setNotification({ message: 'Searching SAM.gov API (Federal)...', type: 'success' });
                        const response = await api.post('/gpss/mining/search-sam-api');
                        setNotification({ 
                          message: `SAM.gov: Found ${response.total_found}, imported ${response.imported} federal opps!`, 
                          type: 'success' 
                        });
                        setTimeout(() => fetchOpportunities(), 3000);
                      } catch (error: any) {
                        setNotification({ message: `SAM.gov error: ${error.message}`, type: 'error' });
                      }
                    }}
                    className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-lg font-bold transition flex items-center gap-2"
                  >
                    <span>🦅</span>
                    <span>Federal</span>
                  </button>
                  <button 
                    onClick={async () => {
                      try {
                        setNotification({ message: 'Mining State & Local portals...', type: 'success' });
                        const response = await api.post('/gpss/mining/mine-state-local');
                        setNotification({ 
                          message: `State/Local: ${response.sources_checked} sources, found ${response.total_found}, imported ${response.imported}!`, 
                          type: 'success' 
                        });
                        setTimeout(() => fetchOpportunities(), 3000);
                      } catch (error: any) {
                        setNotification({ message: `State/Local error: ${error.message}`, type: 'error' });
                      }
                    }}
                    className="bg-orange-600 hover:bg-orange-700 px-5 py-3 rounded-lg font-bold transition flex items-center gap-2"
                  >
                    <span>🏛️</span>
                    <span>State/Local</span>
                  </button>
                  <button 
                    onClick={async () => {
                      try {
                        setNotification({ message: 'Searching GovCon API...', type: 'success' });
                        const response = await api.post('/gpss/mining/search-govcon-api');
                        setNotification({ 
                          message: `GovCon: Found ${response.total_found}, imported ${response.imported}!`, 
                          type: 'success' 
                        });
                        setTimeout(() => fetchOpportunities(), 3000);
                      } catch (error: any) {
                        setNotification({ message: `GovCon error: ${error.message}`, type: 'error' });
                      }
                    }}
                    className="bg-cyan-600 hover:bg-cyan-700 px-4 py-3 rounded-lg font-bold transition flex items-center gap-2"
                  >
                    <span>📊</span>
                    <span>GovCon</span>
                  </button>
                  <button 
                    onClick={async () => {
                      try {
                        setNotification({ message: 'Checking RSS feeds...', type: 'success' });
                        const response = await api.post('/gpss/mining/check-rss-feeds');
                        setNotification({ 
                          message: `RSS: ${response.new_opportunities} from ${response.feeds_checked} feeds.`, 
                          type: 'success' 
                        });
                        setTimeout(() => fetchOpportunities(), 3000);
                      } catch (error: any) {
                        setNotification({ message: `RSS error: ${error.message}`, type: 'error' });
                      }
                    }}
                    className="bg-purple-600 hover:bg-purple-700 px-4 py-3 rounded-lg font-bold transition flex items-center gap-2"
                  >
                    <span>📡</span>
                    <span>RSS</span>
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-2xl font-black text-green-400">6</div>
                  <div className="text-xs text-gray-400">Active Portals</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-2xl font-black text-purple-400">27</div>
                  <div className="text-xs text-gray-400">RSS Feeds</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-2xl font-black text-blue-400">{opportunities.length}</div>
                  <div className="text-xs text-gray-400">Opportunities Found</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-2xl font-black text-yellow-400">Live</div>
                  <div className="text-xs text-gray-400">Status</div>
                </div>
              </div>
            </div>

            {/* Portal Monitor Status */}
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">📡 Portal Monitoring Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { name: 'SAM.gov', icon: '🦅', status: 'online', opportunities: 0, lastScan: 'Ready' },
                  { name: 'GSA eBuy', icon: '⚡', status: 'online', opportunities: 0, lastScan: 'Ready' },
                  { name: 'DIBBS', icon: '🛡️', status: 'online', opportunities: 0, lastScan: 'Ready' },
                  { name: 'Unison Marketplace', icon: '🔷', status: 'online', opportunities: 0, lastScan: 'Ready' },
                  { name: 'SBA SubNet', icon: '🤝', status: 'online', opportunities: 0, lastScan: 'Ready' },
                  { name: 'NECO Cooperative', icon: '🏛️', status: 'online', opportunities: 0, lastScan: 'Ready' }
                ].map((portal, idx) => (
                  <div key={idx} className="bg-gray-700/50 border border-gray-600 px-4 py-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{portal.icon}</span>
                        <span className="font-semibold text-sm">{portal.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-xs text-green-400">LIVE</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-xs text-gray-400">
                      <span>{portal.opportunities} opps</span>
                      <span>{portal.lastScan}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Auto-Mining Active */}
            <div className="mt-6 bg-gradient-to-r from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="text-5xl">✅</div>
                <div>
                  <h3 className="text-xl font-black text-green-400 mb-2">Auto-Mining Engine: ACTIVE</h3>
                  <p className="text-gray-400 text-sm mb-3">
                    Your NEXUS system is now connected to 6 government opportunity portals. Click "Start Auto-Mining" above 
                    to scan all portals and automatically import new opportunities with AI qualification.
                  </p>
                  <div className="flex gap-3">
                    <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">✓ Portal Integration</span>
                    <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">✓ AI Qualification</span>
                    <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">✓ Automated Scoring</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: UPLOAD RFP (Existing - unchanged) */}
        {activeTab === 'upload' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📄 Upload RFP Document</h2>
              <p className="text-gray-400">AI will automatically extract all contacts with categorization</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
              <div 
                className={`border-3 border-dashed ${isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-700/30'} p-12 rounded-xl text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800 transition`}
                onClick={() => document.getElementById('fileInput')?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="text-6xl mb-4">📎</div>
                <h3 className="text-xl font-bold mb-2 text-blue-400">Drop RFP PDF here or click to browse</h3>
                <p className="text-gray-400 mb-4">AI will extract: Contracting Officers, Program Managers, POCs</p>
                <input 
                  type="file" 
                  id="fileInput" 
                  accept=".pdf" 
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>

              {selectedFile && (
                <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
                  <p className="text-green-400 font-semibold">
                    ✅ {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                </div>
              )}

              {selectedFile && !isExtracting && (
                <div className="mt-6 text-center space-y-4">
                  <button
                    onClick={extractContacts}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-bold text-lg transition"
                  >
                    🤖 Extract Contacts with AI
                  </button>

                  <div className="text-sm text-gray-400">
                    <p>Having trouble with PDF extraction?</p>
                    <button
                      onClick={() => {
                        const manualText = prompt(
                          'Paste the contact information from your PDF here:\n\n(Example: John Smith, Contracting Officer, john.smith@defense.gov, (202) 555-0123)',
                          ''
                        );
                        if (manualText && manualText.trim()) {
                          // Process manual text input using JSON endpoint
                          fetch('http://127.0.0.1:8000/extract-contacts', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              document_text: manualText,
                              document_name: `${selectedFile.name}-manual-entry`
                            })
                          })
                          .then(response => response.json())
                          .then(result => {
                            if (result.success) {
                              showNotification(`🎉 Found ${result.contacts_found} contacts! Stored ${result.contacts_stored} in Airtable.`, 'success');
                              setSelectedFile(null);
                              const fileInput = document.getElementById('fileInput') as HTMLInputElement;
                              if (fileInput) fileInput.value = '';
                              setTimeout(() => setActiveTab('contacts'), 2000);
                            } else {
                              showNotification('No contacts found in the provided text', 'error');
                            }
                          })
                          .catch(error => {
                            console.error('Manual extraction error:', error);
                            showNotification('Error processing manual text input', 'error');
                          });
                        }
                      }}
                      className="text-blue-400 hover:text-blue-300 underline ml-2"
                    >
                      📝 Enter Text Manually
                    </button>
                  </div>
                </div>
              )}

              {isExtracting && (
                <div className="mt-6">
                  <div className="bg-blue-900/30 border border-blue-700 p-6 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <div>
                        <h4 className="font-bold text-blue-400 mb-1">Analyzing Document...</h4>
                        <p className="text-sm text-gray-400">Processing document and extracting contacts with AI</p>
                        <div className="mt-2 text-xs text-gray-500">
                          Using advanced AI to find contact information
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB: OPPORTUNITIES - ENHANCED */}
        {activeTab === 'opportunities' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">🎯 All Opportunities</h2>
                <p className="text-gray-400">Federal + State + Local + Cooperative Opportunities</p>
              </div>
              <button 
                onClick={fetchOpportunities}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                🔄 Refresh
              </button>
            </div>

            {/* FILTERS */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="font-bold text-lg mb-4">🔍 Filters</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-400">Source</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={filters.source}
                    onChange={(e) => setFilters({ ...filters, source: e.target.value })}
                  >
                    <option value="all">All Sources</option>
                    <option value="Federal">Federal</option>
                    <option value="State">State</option>
                    <option value="Local">Local</option>
                    <option value="Cooperative">Cooperative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-400">State</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={filters.state}
                    onChange={(e) => setFilters({ ...filters, state: e.target.value })}
                  >
                    <option value="all">All States</option>
                    <option value="Federal">Federal</option>
                    <option value="MI">Michigan</option>
                    <option value="GA">Georgia</option>
                    <option value="MD">Maryland</option>
                    <option value="TX">Texas</option>
                    <option value="CA">California</option>
                    <option value="IL">Illinois</option>
                    <option value="Multi-State">Multi-State</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-400">Urgency</label>
                  <select 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                    value={filters.urgency}
                    onChange={(e) => setFilters({ ...filters, urgency: e.target.value })}
                  >
                    <option value="all">All Urgency</option>
                    <option value="Critical">Critical (&lt; 7 days)</option>
                    <option value="High">High (7-14 days)</option>
                    <option value="Medium">Medium (14-30 days)</option>
                    <option value="Low">Low (30+ days)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-400">&nbsp;</label>
                  <label className="flex items-center gap-2 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 cursor-pointer hover:bg-gray-600">
                    <input 
                      type="checkbox" 
                      checked={filters.edwsbOnly}
                      onChange={(e) => setFilters({ ...filters, edwsbOnly: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span className="text-sm font-semibold text-green-400">EDWOSB Only</span>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2 text-gray-400">&nbsp;</label>
                  <label className="flex items-center gap-2 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 cursor-pointer hover:bg-gray-600">
                    <input 
                      type="checkbox" 
                      checked={filters.homeStatesOnly}
                      onChange={(e) => setFilters({ ...filters, homeStatesOnly: e.target.checked })}
                      className="w-4 h-4"
                    />
                    <span className="text-sm font-semibold text-purple-400">Home States Only</span>
                  </label>
                </div>
              </div>

              {/* Active Filters Display */}
              <div className="mt-4 flex flex-wrap gap-2">
                {filters.source !== 'all' && (
                  <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm font-semibold">
                    Source: {filters.source}
                  </span>
                )}
                {filters.state !== 'all' && (
                  <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm font-semibold">
                    State: {filters.state}
                  </span>
                )}
                {filters.urgency !== 'all' && (
                  <span className="bg-orange-500/20 text-orange-400 px-3 py-1 rounded-full text-sm font-semibold">
                    Urgency: {filters.urgency}
                  </span>
                )}
                {filters.edwsbOnly && (
                  <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm font-semibold">
                    ⭐ EDWOSB Eligible
                  </span>
                )}
                {filters.homeStatesOnly && (
                  <span className="bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full text-sm font-semibold">
                    🏠 Home States Priority
                  </span>
                )}
              </div>
            </div>

            {/* OPPORTUNITIES TABLE */}
            <div className="bg-gray-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Opportunity</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Source</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Agency</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Value</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Due Date</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Score</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                      <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredOpportunities.map(opp => (
                      <tr key={opp.id} className="border-t border-gray-700 hover:bg-gray-700/50 cursor-pointer">
                        <td className="px-6 py-4">
                          <div className="flex items-start gap-2 mb-2">
                            {opp.edwsbEligible && (
                              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/30 font-bold">
                                EDWOSB
                              </span>
                            )}
                            {opp.homeStatePriority && (
                              <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30 font-bold">
                                HOME
                              </span>
                            )}
                          </div>
                          <div className="font-bold text-blue-400">{opp.title}</div>
                          <div className="text-sm text-gray-400">{opp.rfpNumber}</div>
                          <div className="text-xs text-gray-500 mt-1">{opp.category}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-purple-400">{opp.source}</div>
                          <div className="text-xs text-gray-500">{opp.sourcePortal}</div>
                          <div className="text-xs text-gray-500 mt-1">{opp.state}</div>
                        </td>
                        <td className="px-6 py-4 text-gray-300">{opp.agency}</td>
                        <td className="px-6 py-4">
                          <div className="text-green-400 font-bold text-lg">{formatCurrency(opp.value)}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-gray-300">{opp.dueDate}</div>
                          <span className={`inline-block mt-1 text-xs font-bold px-2 py-1 rounded border ${getUrgencyColor(opp.urgency)}`}>
                            {opp.urgency}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-2xl font-black text-yellow-400">{opp.priorityScore}</div>
                          <div className="text-xs text-gray-500">/ 100</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="bg-gray-600 text-gray-300 px-3 py-1 rounded-full text-sm font-semibold">
                            {opp.internalStatus}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                setPricingOpportunity(opp);
                                setShowPricingCalculator(true);
                              }}
                              className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                            >
                              💰 Price
                            </button>
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                generateProposal(opp);
                              }}
                              disabled={generatingProposal}
                              className={`${generatingProposal ? 'bg-gray-600 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'} px-4 py-2 rounded-lg font-semibold transition`}
                            >
                              {generatingProposal ? '⏳ Generating...' : '🚀 Proposal'}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {filteredOpportunities.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4 opacity-20">🔍</div>
                  <p className="text-gray-500 font-semibold">No opportunities match your filters</p>
                  <button 
                    onClick={() => setFilters({ source: 'all', state: 'all', edwsbOnly: false, urgency: 'all', homeStatesOnly: false })}
                    className="mt-4 text-blue-400 hover:text-blue-300 font-semibold"
                  >
                    Clear All Filters
                  </button>
                </div>
              )}
            </div>

            {/* Summary Footer */}
            <div className="mt-4 text-sm text-gray-500 text-center">
              Showing {filteredOpportunities.length} of {opportunities.length} opportunities • 
              Total Pipeline Value: <span className="font-bold text-green-400">{formatCurrency(filteredOpportunities.reduce((sum, o) => sum + o.value, 0))}</span>
            </div>
          </div>
        )}

        {/* TAB: PROPOSALS */}
        {activeTab === 'proposals' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">📝 Proposals & Quotes</h2>
                <p className="text-gray-400">AI-generated government proposals with compliance checking</p>
              </div>
              <button 
                onClick={fetchProposals}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                🔄 Refresh
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Total Proposals</h3>
                <p className="text-4xl font-bold mb-1">{proposals.length}</p>
                <p className="text-sm text-white/70">All Time</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Sent</h3>
                <p className="text-4xl font-bold mb-1">{proposals.filter(p => p.status === 'Sent' || p.status === 'Under Review').length}</p>
                <p className="text-sm text-white/70">Awaiting Response</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Accepted</h3>
                <p className="text-4xl font-bold mb-1">{proposals.filter(p => p.status === 'Accepted').length}</p>
                <p className="text-sm text-white/70">Won</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Win Rate</h3>
                <p className="text-4xl font-bold mb-1">
                  {proposals.length > 0 ? Math.round((proposals.filter(p => p.status === 'Accepted').length / proposals.length) * 100) : 0}%
                </p>
                <p className="text-sm text-white/70">Success Rate</p>
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
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Due Date</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {proposals.map(proposal => (
                        <tr key={proposal.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                          <td className="px-6 py-4">
                            <div className="font-bold text-blue-400">{proposal.proposalName}</div>
                            <div className="text-sm text-gray-400">{proposal.rfpNumber}</div>
                            <div className="text-xs text-gray-500 mt-1">Generated: {new Date(proposal.generatedDate).toLocaleDateString()}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-300">{proposal.agency}</td>
                          <td className="px-6 py-4">
                            <div className="text-green-400 font-bold text-lg">{formatCurrency(proposal.value)}</div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                              proposal.status === 'Accepted' ? 'bg-green-500/20 text-green-400' :
                              proposal.status === 'Sent' || proposal.status === 'Under Review' ? 'bg-blue-500/20 text-blue-400' :
                              proposal.status === 'Rejected' ? 'bg-red-500/20 text-red-400' :
                              'bg-gray-500/20 text-gray-400'
                            }`}>
                              {proposal.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-300">{proposal.dueDate}</td>
                          <td className="px-6 py-4">
                            <div className="flex gap-2">
                              <button 
                                onClick={() => {
                                  setSelectedProposal(proposal);
                                  setShowProposalModal(true);
                                }}
                                className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm font-semibold transition"
                              >
                                View
                              </button>
                              <button 
                                onClick={() => exportProposalPDF(proposal)}
                                className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm font-semibold transition"
                              >
                                Export
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
                  <div className="text-6xl mb-4 opacity-20">📝</div>
                  <p className="text-gray-500 font-semibold mb-4">No proposals yet</p>
                  <p className="text-sm text-gray-600 mb-6">Generate your first proposal from the Opportunities tab</p>
                  <button 
                    onClick={() => setActiveTab('opportunities')}
                    className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                  >
                    Go to Opportunities →
                  </button>
                </div>
              )}
            </div>

            {/* Info Banner */}
            <div className="mt-6 bg-blue-900/30 border border-blue-700 rounded-xl p-6">
              <h3 className="text-lg font-bold text-blue-400 mb-3">How Proposal Generation Works:</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-3xl mb-2">🎯</div>
                  <p className="font-semibold mb-1">1. Select Opportunity</p>
                  <p className="text-gray-400">Choose from opportunities tab</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">🤖</div>
                  <p className="font-semibold mb-1">2. AI Generates</p>
                  <p className="text-gray-400">Claude creates compliant proposal</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">✏️</div>
                  <p className="font-semibold mb-1">3. Review & Edit</p>
                  <p className="text-gray-400">Customize before sending</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">📤</div>
                  <p className="font-semibold mb-1">4. Export & Send</p>
                  <p className="text-gray-400">Download PDF and submit</p>
                </div>
              </div>
            </div>
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
        {activeTab === 'products' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">📦 Products Catalog</h2>
                <p className="text-gray-400">Your service offerings and pricing</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => openProductModal()}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  ➕ Add Product
                </button>
                <button 
                  onClick={fetchProducts}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  🔄 Refresh
                </button>
              </div>
            </div>

            {productsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400">Loading products...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.length > 0 ? (
                  products.map(product => (
                    <div key={product.id} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-blue-400 mb-1">{product.name}</h3>
                          <p className="text-sm text-gray-400">{product.category || 'Uncategorized'}</p>
                        </div>
                        <div className="text-2xl font-bold text-green-400">
                          ${product.basePrice?.toLocaleString() || 0}
                        </div>
                      </div>
                      <p className="text-sm text-gray-300 mb-4 line-clamp-2">{product.description || 'No description'}</p>
                      <div className="flex gap-2 mt-4">
                        <button 
                          onClick={() => openProductModal(product)}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition text-sm"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => deleteProduct(product.id)}
                          className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold transition text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-full text-center py-12 bg-gray-800 rounded-xl">
                    <div className="text-6xl mb-4 opacity-20">📦</div>
                    <p className="text-gray-500 font-semibold mb-4">No products yet</p>
                    <p className="text-sm text-gray-600 mb-6">Add your service offerings to the catalog</p>
                    <button 
                      onClick={() => openProductModal()}
                      className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                    >
                      ➕ Add First Product
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: ANALYTICS */}
        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📈 Analytics & Insights</h2>
              <p className="text-gray-400">Performance metrics and trends</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Total Opportunities</h3>
                <p className="text-4xl font-bold mb-1">{opportunities.length}</p>
                <p className="text-sm text-white/70">All Time</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Pipeline Value</h3>
                <p className="text-4xl font-bold mb-1">{formatCurrency(stats.totalPipeline)}</p>
                <p className="text-sm text-white/70">Total Value</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Proposals Sent</h3>
                <p className="text-4xl font-bold mb-1">{proposals.length}</p>
                <p className="text-sm text-white/70">All Time</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold text-white/80 mb-2">Win Rate</h3>
                <p className="text-4xl font-bold mb-1">
                  {proposals.length > 0 ? Math.round((proposals.filter(p => p.status === 'Accepted').length / proposals.length) * 100) : 0}%
                </p>
                <p className="text-sm text-white/70">Success Rate</p>
              </div>
            </div>

            {/* Source Breakdown */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Opportunity Sources</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { name: 'Federal', count: opportunities.filter(o => o.source === 'Federal').length, color: 'blue' },
                  { name: 'State', count: opportunities.filter(o => o.source === 'State').length, color: 'purple' },
                  { name: 'Local', count: opportunities.filter(o => o.source === 'Local').length, color: 'orange' },
                  { name: 'Cooperative', count: opportunities.filter(o => o.source === 'Cooperative').length, color: 'green' }
                ].map((source, idx) => (
                  <div key={idx} className={`bg-${source.color}-900/30 border border-${source.color}-700/50 px-4 py-4 rounded-lg`}>
                    <div className="text-3xl font-bold mb-2">{source.count}</div>
                    <div className={`text-sm font-semibold text-${source.color}-400`}>{source.name}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* EDWOSB Performance */}
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">EDWOSB Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-green-900/30 border border-green-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-green-400">{stats.edwsbSetAsides}</div>
                  <div className="text-sm text-gray-300">EDWOSB Eligible</div>
                </div>
                <div className="bg-blue-900/30 border border-blue-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-blue-400">
                    {stats.edwsbSetAsides > 0 ? Math.round((stats.edwsbSetAsides / opportunities.length) * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-300">Of Total Pipeline</div>
                </div>
                <div className="bg-purple-900/30 border border-purple-700/50 px-4 py-4 rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-purple-400">
                    {formatCurrency(opportunities.filter(o => o.edwsbEligible).reduce((sum, o) => sum + o.value, 0))}
                  </div>
                  <div className="text-sm text-gray-300">EDWOSB Pipeline Value</div>
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
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
          <div className="bg-gray-800 rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 sticky top-0 z-10">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2">{selectedProposal.proposalName}</h2>
                  <div className="flex gap-4 text-sm">
                    <span className="text-white/80">RFP: {selectedProposal.rfpNumber}</span>
                    <span className="text-white/80">•</span>
                    <span className="text-white/80">Value: ${selectedProposal.value.toLocaleString()}</span>
                    <span className="text-white/80">•</span>
                    <span className="text-white/80">Due: {selectedProposal.dueDate}</span>
                  </div>
                </div>
                <button 
                  onClick={() => setShowProposalModal(false)}
                  className="text-white hover:text-gray-300 text-3xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Executive Summary */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-blue-400 mb-3 flex items-center gap-2">
                  <span>📋</span> Executive Summary
                </h3>
                <p className="text-gray-300 whitespace-pre-wrap">{selectedProposal.executiveSummary}</p>
              </div>

              {/* Technical Approach */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-green-400 mb-3 flex items-center gap-2">
                  <span>🔧</span> Technical Approach
                </h3>
                <p className="text-gray-300 whitespace-pre-wrap">{selectedProposal.technicalApproach}</p>
              </div>

              {/* Staffing Plan */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-purple-400 mb-3 flex items-center gap-2">
                  <span>👥</span> Staffing Plan
                </h3>
                <p className="text-gray-300 whitespace-pre-wrap">{selectedProposal.staffingPlan}</p>
              </div>

              {/* Past Performance */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-yellow-400 mb-3 flex items-center gap-2">
                  <span>⭐</span> Past Performance
                </h3>
                <p className="text-gray-300 whitespace-pre-wrap">{selectedProposal.pastPerformance}</p>
              </div>

              {/* Pricing with Intelligent Breakdown */}
              <div className="bg-gradient-to-br from-green-900/30 to-green-700/30 border border-green-600 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-green-400 mb-3 flex items-center gap-2">
                  <span>💰</span> Intelligent Pricing
                </h3>
                <div className="text-4xl font-black text-green-400 mb-4">
                  ${selectedProposal.pricingTotal.toLocaleString()}
                </div>
                
                {/* Cost Breakdown */}
                {selectedProposal.pricingBreakdown && (selectedProposal.pricingBreakdown as any).labor !== undefined && (
                  <div className="mb-4 bg-gray-800/50 p-4 rounded-lg">
                    <div className="text-sm font-bold text-green-400 mb-2">Cost Breakdown:</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="text-gray-400">Labor:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).labor || 0).toLocaleString()}</div>
                      
                      <div className="text-gray-400">Materials:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).materials || 0).toLocaleString()}</div>
                      
                      <div className="text-gray-400">Other Costs:</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).other || 0).toLocaleString()}</div>
                      
                      <div className="text-gray-400 pt-2 border-t border-gray-600">Subtotal:</div>
                      <div className="text-white font-semibold pt-2 border-t border-gray-600">${((selectedProposal.pricingBreakdown as any).subtotal || 0).toLocaleString()}</div>
                      
                      <div className="text-gray-400">Overhead ({(selectedProposal.pricingBreakdown as any).overhead_rate || 0}%):</div>
                      <div className="text-white font-semibold">${((selectedProposal.pricingBreakdown as any).overhead_amount || 0).toLocaleString()}</div>
                      
                      <div className="text-yellow-400 font-bold pt-2 border-t border-gray-600">Total Cost:</div>
                      <div className="text-yellow-400 font-bold pt-2 border-t border-gray-600">${((selectedProposal.pricingBreakdown as any).total_cost || 0).toLocaleString()}</div>
                      
                      <div className="text-green-400 font-bold text-base pt-2 border-t-2 border-green-600">Bid Price:</div>
                      <div className="text-green-400 font-bold text-base pt-2 border-t-2 border-green-600">${selectedProposal.pricingTotal.toLocaleString()}</div>
                    </div>
                  </div>
                )}
                
                <p className="text-gray-300 text-sm whitespace-pre-wrap">{selectedProposal.pricingJustification}</p>
              </div>

              {/* Compliance Checklist */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-blue-400 mb-3 flex items-center gap-2">
                  <span>✅</span> Compliance Checklist
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(selectedProposal.complianceChecklist || {}).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2">
                      <span className={`text-2xl ${value ? 'text-green-400' : 'text-red-400'}`}>
                        {value ? '✓' : '✗'}
                      </span>
                      <span className="text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recipients */}
              <div className="bg-gray-700 p-6 rounded-xl">
                <h3 className="text-xl font-bold text-purple-400 mb-3 flex items-center gap-2">
                  <span>📧</span> Recipients
                </h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-400">To:</span>
                    <span className="ml-2 text-blue-400 font-semibold">{selectedProposal.recipients?.primary_to || 'Not specified'}</span>
                  </div>
                  {selectedProposal.recipients?.cc && (
                    <div>
                      <span className="text-gray-400">CC:</span>
                      <span className="ml-2 text-gray-300">{Array.isArray(selectedProposal.recipients.cc) ? selectedProposal.recipients.cc.join(', ') : selectedProposal.recipients.cc}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="bg-gray-700 p-6 flex gap-4 justify-between sticky bottom-0">
              <button 
                onClick={() => {
                  // Use RFP content if available, otherwise use placeholder
                  setComplianceRfpContent('RFP content would be loaded here');
                  setShowComplianceChecker(true);
                }}
                className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-semibold transition"
              >
                ✅ Check Compliance
              </button>
              <div className="flex gap-4">
                <button 
                  onClick={() => setShowProposalModal(false)}
                  className="bg-gray-600 hover:bg-gray-500 px-6 py-3 rounded-lg font-semibold transition"
                >
                  Close
                </button>
                <button 
                  onClick={() => saveProposal(selectedProposal)}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  💾 Save to Airtable
                </button>
                <button 
                  onClick={() => exportProposalPDF(selectedProposal)}
                  className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  📄 Export PDF
                </button>
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

