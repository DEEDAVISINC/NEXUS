const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

export class ApiClient {
  static async get(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    return response.json();
  }

  static async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  static async put(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  static async patch(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  static async delete(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
    });
    return response.json();
  }
}

// API Functions
export const api = {
  // Generic methods
  get: (endpoint: string) => ApiClient.get(endpoint),
  post: (endpoint: string, data?: any) => ApiClient.post(endpoint, data || {}),
  put: (endpoint: string, data: any) => ApiClient.put(endpoint, data),
  patch: (endpoint: string, data: any) => ApiClient.patch(endpoint, data),
  delete: (endpoint: string) => ApiClient.delete(endpoint),

  // Health
  getHealth: () => ApiClient.get('/health'),

  // Dashboard
  getDashboardStats: () => ApiClient.get('/dashboard/stats'),
  getDashboardActivity: () => ApiClient.get('/dashboard/activity'),
  getDashboardAlerts: () => ApiClient.get('/dashboard/alerts'),
  getCalendarEvents: () => ApiClient.get('/calendar/events'),
  getTransportationNotifications: () => ApiClient.get('/transportation-logistics/notifications'),

  // NEXUS Core
  extractContacts: (data: {document_text: string, document_name: string}) =>
    ApiClient.post('/extract-contacts', data),

  // GPSS
  qualifyOpportunity: (opportunityId: string) =>
    ApiClient.post('/qualify-opportunity', {opportunity_id: opportunityId}),
  generateQuote: (opportunityId: string) =>
    ApiClient.post('/generate-quote', {opportunity_id: opportunityId}),

  // DDCSS
  qualifyProspect: (prospectId: string) =>
    ApiClient.post('/ddcss/qualify-prospect', {prospect_id: prospectId}),
  generateBlueprint: (prospectId: string, frameworkType: string) =>
    ApiClient.post('/ddcss/generate-blueprint', {prospect_id: prospectId, framework_type: frameworkType}),
  analyzeResponse: (emailContent: string, prospectId?: string) =>
    ApiClient.post('/ddcss/analyze-response', {email_content: emailContent, prospect_id: prospectId}),
  aiChat: (message: string, sessionId?: string) =>
    ApiClient.post('/ai/chat', {message, session_id: sessionId}),

  // ATLAS PM
  getProjects: () => ApiClient.get('/atlas/projects'),
  createProject: (data: any) => ApiClient.post('/atlas/projects', data),
  getProject: (id: string) => ApiClient.get(`/atlas/projects/${id}`),
  updateProject: (id: string, data: any) => ApiClient.put(`/atlas/projects/${id}`, data),

  getRfps: (projectId?: string) =>
    ApiClient.get(projectId ? `/atlas/rfps?project_id=${projectId}` : '/atlas/rfps'),
  createRfp: (data: any) => ApiClient.post('/atlas/rfps', data),

  getChangeOrders: (projectId?: string) =>
    ApiClient.get(projectId ? `/atlas/change-orders?project_id=${projectId}` : '/atlas/change-orders'),
  createChangeOrder: (data: any) => ApiClient.post('/atlas/change-orders', data),

  analyzeRfp: (rfpContent: string, projectId?: string) =>
    ApiClient.post('/atlas/analyze-rfp', {rfp_content: rfpContent, project_id: projectId}),
  generateWbs: (projectId: string) =>
    ApiClient.post('/atlas/generate-wbs', {project_id: projectId}),
  analyzeChangeRequest: (description: string, projectId: string) =>
    ApiClient.post('/atlas/analyze-change-request', {change_description: description, project_id: projectId}),

  // Task Board API
  getTasks: (projectId?: string) =>
    ApiClient.get(projectId ? `/atlas/tasks?project_id=${projectId}` : '/atlas/tasks'),
  createTask: (data: any) => ApiClient.post('/atlas/tasks', data),
  updateTask: (id: string, data: any) => ApiClient.put(`/atlas/tasks/${id}`, data),
  deleteTask: (id: string) => ApiClient.delete(`/atlas/tasks/${id}`),
  getAITaskSuggestions: (tasks: any[]) => 
    ApiClient.post('/atlas/tasks/ai-suggestions', {tasks}),
  autoGenerateTasks: (description: string, projectName: string) =>
    ApiClient.post('/atlas/tasks/auto-generate', {description, project_name: projectName}),

  // Vendor Portals API
  getVendorPortals: (category?: string, search?: string) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    const query = params.toString();
    return ApiClient.get(`/vendor-portals${query ? `?${query}` : ''}`);
  },
  createVendorPortal: (data: any) => ApiClient.post('/vendor-portals', data),
  updateVendorPortal: (id: string, data: any) => ApiClient.put(`/vendor-portals/${id}`, data),
  deleteVendorPortal: (id: string) => ApiClient.delete(`/vendor-portals/${id}`),

  // GPSS Opportunities API
  getGpssOpportunities: (filters?: {
    view?: string;
    source?: string;
    state?: string;
    edwsb_only?: boolean;
    urgency?: string;
    home_states_only?: boolean;
  }) => {
    const params = new URLSearchParams();
    if (filters?.view) params.append('view', filters.view);
    if (filters?.source) params.append('source', filters.source);
    if (filters?.state) params.append('state', filters.state);
    if (filters?.edwsb_only) params.append('edwsb_only', 'true');
    if (filters?.urgency) params.append('urgency', filters.urgency);
    if (filters?.home_states_only) params.append('home_states_only', 'true');
    const query = params.toString();
    return ApiClient.get(`/gpss/opportunities${query ? `?${query}` : ''}`);
  },
  createGpssOpportunity: (data: any) => ApiClient.post('/gpss/opportunities', data),
  uploadAndAnalyzeRfp: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/gpss/upload-rfp`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Upload failed' }));
      throw new Error(err.error || `Upload failed (${response.status})`);
    }
    return response.json();
  },
  updateGpssOpportunity: (id: string, data: any) => ApiClient.put(`/gpss/opportunities/${id}`, data),
  getGpssStats: () => ApiClient.get('/gpss/stats'),
  
  // GPSS Suppliers
  getGpssSuppliers: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
    }
    const query = params.toString();
    return ApiClient.get(`/gpss/suppliers${query ? `?${query}` : ''}`);
  },
  createGpssSupplier: (data: any) => ApiClient.post('/gpss/suppliers', data),
  updateGpssSupplier: (id: string, data: any) => ApiClient.put(`/gpss/suppliers/${id}`, data),
  findSuppliersForProduct: (product: string, category?: string, autoMine?: boolean) =>
    ApiClient.post('/gpss/suppliers/find-for-product', { product, category, auto_mine: autoMine !== false }),
  mineSuppliersThomasnet: (product: string) =>
    ApiClient.post('/gpss/suppliers/mine-thomasnet', { product }),
  mineSuppliersGoogle: (product: string) =>
    ApiClient.post('/gpss/suppliers/mine-google', { product }),
  mineSuppliersGsa: (product: string) =>
    ApiClient.post('/gpss/suppliers/mine-gsa', { product }),
  mineSuppliersAll: (product: string, category?: string) =>
    ApiClient.post('/gpss/suppliers/mine-all', { product, category }),
  importSuppliersCsv: async (file: File, fieldMapping?: Record<string, string>) => {
    const formData = new FormData();
    formData.append('file', file);
    if (fieldMapping) formData.append('field_mapping', JSON.stringify(fieldMapping));
    const response = await fetch(`${API_BASE}/gpss/suppliers/import-csv`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Import failed' }));
      throw new Error(err.error || `Import failed (${response.status})`);
    }
    return response.json();
  },
  
  // PRISM Notifications & Receipt Tracking
  getNotifications: (target?: string, limit?: number) => {
    const params = new URLSearchParams();
    if (target) params.append('target', target);
    if (limit) params.append('limit', String(limit));
    const query = params.toString();
    return ApiClient.get(`/prism/notifications${query ? `?${query}` : ''}`);
  },
  markNotificationsRead: (ids?: string[]) =>
    ApiClient.post('/prism/notifications/read', ids ? { notification_ids: ids } : { mark_all: true }),
  uploadReceipt: async (formData: FormData) => {
    const response = await fetch(`${API_BASE}/prism/receipt/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },
  getTracking: (orderId: string) => ApiClient.get(`/prism/tracking/${orderId}`),
  updateTracking: (orderId: string, data: any) => ApiClient.put(`/prism/tracking/${orderId}`, data),

  // GPSS Proposals API
  getGpssProposals: () => ApiClient.get('/gpss/proposals'),
  saveGpssProposal: (data: any) => ApiClient.post('/gpss/proposals', data),
  
  // GPSS Pricing Intelligence API
  calculateIntelligentPricing: (opportunityId: string, serviceCategory?: string) =>
    ApiClient.post('/gpss/pricing/calculate', {opportunity_id: opportunityId, service_category: serviceCategory}),
  getPricingHistory: (filters?: {service_category?: string, win_loss?: string}) => {
    const params = new URLSearchParams();
    if (filters?.service_category) params.append('service_category', filters.service_category);
    if (filters?.win_loss) params.append('win_loss', filters.win_loss);
    const query = params.toString();
    return ApiClient.get(`/gpss/pricing/history${query ? `?${query}` : ''}`);
  },
  
  // GPSS Compliance Checker API
  analyzeRfpCompliance: (rfpContent: string, rfpId?: string) =>
    ApiClient.post('/gpss/compliance/analyze-rfp', {rfp_content: rfpContent, rfp_id: rfpId}),
  checkProposalCompliance: (proposalData: any, rfpRequirements: any) =>
    ApiClient.post('/gpss/compliance/check-proposal', {proposal_data: proposalData, rfp_requirements: rfpRequirements}),
  
  // GPSS Opportunity Mining & Forecasting API
  getMiningStatus: () => ApiClient.get('/gpss/mining/status'),
  minePortal: (portalId: string) =>
    ApiClient.post(`/gpss/mining/portal/${portalId}`, {}),
  autoMineAll: () =>
    ApiClient.post('/gpss/mining/auto-mine-all', {}),
  scrapeTarget: (targetId: string) =>
    ApiClient.post(`/gpss/mining/target/${targetId}`, {}),
  scrapeAllTargets: () =>
    ApiClient.post('/gpss/mining/scrape-all-targets', {}),
  mineAgencyForecasts: () =>
    ApiClient.post('/gpss/forecasting/mine', {}),
  mineEdwosbOpportunities: () =>
    ApiClient.post('/gpss/mining/mine-edwosb', {}),
  compareQuotes: (opportunityId: string) =>
    ApiClient.get(`/gpss/supplier-quotes/compare/${opportunityId}`),
  rateSupplier: (supplierId: string, outcome: string) =>
    ApiClient.post(`/gpss/suppliers/${supplierId}/rate`, { outcome }),
  generateForecasts: (agencyName?: string, lookbackMonths?: number) =>
    ApiClient.post('/gpss/forecasting/generate', {agency_name: agencyName, lookback_months: lookbackMonths}),
  analyzeAgency: (agencyName: string) =>
    ApiClient.get(`/gpss/forecasting/agency-analysis/${encodeURIComponent(agencyName)}`),
  getCompetitorIntel: (competitorName: string, keywords?: string) => {
    const params = new URLSearchParams();
    if (keywords) params.append('keywords', keywords);
    const query = params.toString();
    return ApiClient.get(`/gpss/intelligence/competitor/${encodeURIComponent(competitorName)}${query ? `?${query}` : ''}`);
  },
  generateAlerts: () =>
    ApiClient.get('/gpss/alerts/generate'),

  // Invoices
  getInvoices: (filters?: {status?: string, source_system?: string, client_type?: string}) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.source_system) params.append('source_system', filters.source_system);
    if (filters?.client_type) params.append('client_type', filters.client_type);
    const query = params.toString();
    return ApiClient.get(`/invoices${query ? `?${query}` : ''}`);
  },
  getInvoice: (invoiceId: string) =>
    ApiClient.get(`/invoices/${invoiceId}`),
  generateInvoiceFromOpportunity: (opportunityId: string) =>
    ApiClient.post(`/invoices/generate/opportunity/${opportunityId}`, {}),
  generateInvoiceFromProject: (projectId: string) =>
    ApiClient.post(`/invoices/generate/project/${projectId}`, {}),
  generateInvoiceFromProspect: (prospectId: string) =>
    ApiClient.post(`/invoices/generate/prospect/${prospectId}`, {}),
  updateInvoice: (invoiceId: string, updates: any) =>
    ApiClient.put(`/invoices/${invoiceId}`, updates),
  deleteInvoice: (invoiceId: string) =>
    ApiClient.delete(`/invoices/${invoiceId}`),
  sendInvoice: (invoiceId: string, email: string, message?: string) =>
    ApiClient.post(`/invoices/${invoiceId}/send`, {email, message}),

  // GPSS Contacts API
  getGpssContacts: () => ApiClient.get('/gpss/contacts'),
  createGpssContact: (data: any) => ApiClient.post('/gpss/contacts', data),
  updateGpssContact: (id: string, data: any) => ApiClient.put(`/gpss/contacts/${id}`, data),
  deleteGpssContact: (id: string) => ApiClient.delete(`/gpss/contacts/${id}`),

  // GPSS Products API
  getGpssProducts: () => ApiClient.get('/gpss/products'),
  createGpssProduct: (data: any) => ApiClient.post('/gpss/products', data),
  updateGpssProduct: (id: string, data: any) => ApiClient.put(`/gpss/products/${id}`, data),
  deleteGpssProduct: (id: string) => ApiClient.delete(`/gpss/products/${id}`),

  // GPSS Subcontractors API
  getGpssSubcontractors: () => ApiClient.get('/gpss/subcontractors'),
  createGpssSubcontractor: (data: any) => ApiClient.post('/gpss/subcontractors', data),
  updateGpssSubcontractor: (id: string, data: any) => ApiClient.put(`/gpss/subcontractors/${id}`, data),
  deleteGpssSubcontractor: (id: string) => ApiClient.delete(`/gpss/subcontractors/${id}`),
  findSubcontractors: (serviceType: string, location: string, radiusMiles: number = 25) =>
    ApiClient.post('/gpss/subcontractors/find', { service_type: serviceType, location, radius_miles: radiusMiles }),
  searchSubcontractorsDatabase: (serviceType?: string, location?: string) =>
    ApiClient.post('/gpss/subcontractors/search', { service_type: serviceType, location }),

  // Workflow Management API (live folder scanning)
  getWorkflowQueues: () => ApiClient.get('/api/workflow/queues'),
  getBidsDashboard: () => ApiClient.get('/api/bids/dashboard'),
  getBidsScan: () => ApiClient.get('/api/bids/scan'),
  getBidsAlerts: () => ApiClient.get('/api/bids/alerts'),
  reviewOpportunity: (opportunityId: string, data: {name: string, decision: 'pursue' | 'skip', notes?: string}) =>
    ApiClient.post(`/api/workflow/opportunity/${opportunityId}/review`, data),
  identifySuppliers: (opportunityId: string, supplierIds: string[]) =>
    ApiClient.post(`/api/workflow/opportunity/${opportunityId}/suppliers`, {supplierIds}),
  markQuotesRequested: (opportunityId: string, count: number) =>
    ApiClient.post(`/api/workflow/opportunity/${opportunityId}/quotes-requested`, {count}),
  advanceWorkflow: (opportunityId: string, newStatus: string) =>
    ApiClient.post(`/api/workflow/opportunity/${opportunityId}/advance`, {newStatus}),

  // DDCSS Prospects API
  getDdcssProspects: () => ApiClient.get('/ddcss/prospects'),
  createDdcssProspect: (data: any) => ApiClient.post('/ddcss/prospects', data),

  // DDCSS Tools API
  getDdcssClientAvatars: () => ApiClient.get('/ddcss/client-avatars'),
  createDdcssClientAvatar: (data: any) => ApiClient.post('/ddcss/client-avatars', data),
  updateDdcssClientAvatar: (id: string, data: any) => ApiClient.put(`/ddcss/client-avatars/${id}`, data),
  deleteDdcssClientAvatar: (id: string) => ApiClient.delete(`/ddcss/client-avatars/${id}`),
  createDdcssSuccessPath: (data: any) => ApiClient.post('/ddcss/success-paths', data),
  createDdcssPitchmap: (data: any) => ApiClient.post('/ddcss/pitchmaps', data),

  // Mining Targets API
  getMiningTargets: () => ApiClient.get('/gpss/mining/targets'),
  createMiningTarget: (data: any) => ApiClient.post('/gpss/mining/targets', data),
  updateMiningTarget: (id: string, data: any) => ApiClient.put(`/gpss/mining/targets/${id}`, data),
  deleteMiningTarget: (id: string) => ApiClient.delete(`/gpss/mining/targets/${id}`),

  // AI Conversations
  createConversation: (data: any) => ApiClient.post('/ai/conversations', data),
  updateConversation: (sessionId: string, data: any) => ApiClient.put(`/ai/conversations/${sessionId}`, data),
  getConversation: (sessionId: string) => ApiClient.get(`/ai/conversations/${sessionId}`),
  getAllConversations: () => ApiClient.get('/ai/conversations'),

  // GBIS (Grant Business Intelligence System)
  getGbisOpportunities: (filters?: {
    priorityLevel?: string;
    funderType?: string;
    division?: string;
    status?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.priorityLevel && filters.priorityLevel !== 'all') params.append('priority_level', filters.priorityLevel);
    if (filters?.funderType && filters.funderType !== 'all') params.append('funder_type', filters.funderType);
    if (filters?.division && filters.division !== 'all') params.append('division', filters.division);
    if (filters?.status && filters.status !== 'all') params.append('status', filters.status);
    const query = params.toString();
    return ApiClient.get(`/gbis/opportunities${query ? `?${query}` : ''}`);
  },
  getGbisApplications: (filters?: {status?: string}) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    const query = params.toString();
    return ApiClient.get(`/gbis/applications${query ? `?${query}` : ''}`);
  },
  getGbisPipeline: () => ApiClient.get('/gbis/pipeline'),
  getGbisStoryLibrary: () => ApiClient.get('/gbis/story-library'),
  getGbisStats: () => ApiClient.get('/gbis/stats'),
  calculateGrantScore: (opportunityData: any) =>
    ApiClient.post('/gbis/calculate-score', opportunityData),
  generateGrantApplication: (opportunityId: string) =>
    ApiClient.post('/gbis/generate-application', {opportunity_id: opportunityId}),
  mineGrantSource: (sourceId: string) =>
    ApiClient.post('/gbis/mine-source', {target_id: sourceId}),

  // GBIS Mining — discovery triggers
  gbisRunAll: () =>
    ApiClient.post('/gbis/mine-all', {}),
  gbisMineSource: (sourceType: 'michigan_foundations' | 'veteran_grants' | 'grants_gov' | 'all') =>
    ApiClient.post('/gbis/mine-source', {source_type: sourceType}),
  gbisSeedMichiganFoundations: () =>
    ApiClient.post('/gbis/research-lane/seed-foundations', {}),
  gbisSeedVeteranSources: () =>
    ApiClient.post('/gbis/research-lane/seed-veteran-sources', {}),
  gbisMineFederal: () =>
    ApiClient.post('/gbis/research-lane/mine-federal', {}),
  gbisGetResearchLane: (entity?: string) => {
    const query = entity ? `?entity=${encodeURIComponent(entity)}` : '';
    return ApiClient.get(`/gbis/research-lane/opportunities${query}`);
  },

  // GBIS Small Business Grants
  gbisSeedSmallGrants: () =>
    ApiClient.post('/gbis/mine-small-grants/seed', {}),
  gbisSeedSmallGrantsFreeOnly: () =>
    ApiClient.post('/gbis/mine-small-grants/seed-free', {}),
  gbisSmallGrantsDailyDigest: () =>
    ApiClient.get('/gbis/mine-small-grants/daily-digest'),

  // VERTEX Financial System - Essential endpoints only
  createVertexExpense: (data: any) => ApiClient.post('/vertex/expenses', data),
  exportToQuickBooks: (data: any) => ApiClient.post('/vertex/export/quickbooks', data),
  getVertexDashboard: () => ApiClient.get('/vertex/dashboard'),
  getVertexInvoices: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
    }
    const query = params.toString();
    return ApiClient.get(`/vertex/invoices${query ? `?${query}` : ''}`);
  },
  getVertexExpenses: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
    }
    const query = params.toString();
    return ApiClient.get(`/vertex/expenses${query ? `?${query}` : ''}`);
  },
  getVertexRevenue: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
    }
    const query = params.toString();
    return ApiClient.get(`/vertex/revenue${query ? `?${query}` : ''}`);
  },
  getProfitLossStatement: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString();
    return ApiClient.get(`/vertex/reports/pl${query ? `?${query}` : ''}`);
  },
  getFinancialHealthScore: () => ApiClient.get('/vertex/ai/financial-health'),
  updateVertexExpense: (expenseId: string, data: any) => ApiClient.put(`/vertex/expenses/${expenseId}`, data),
  getRevenueSummary: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString();
    return ApiClient.get(`/vertex/revenue/summary${query ? `?${query}` : ''}`);
  },

  // ═══════════════════════════════════════════════════════════
  // VERTEX FINANCING — SouthStar Capital & Bankers Factoring
  // ═══════════════════════════════════════════════════════════
  getFinancingReferrals: () => ApiClient.get('/vertex/financing/referrals'),
  createFinancingReferral: (data: any) => ApiClient.post('/vertex/financing/referrals', data),
  updateFinancingReferral: (referralId: string, data: any) => ApiClient.put(`/vertex/financing/referrals/${referralId}`, data),
  deleteFinancingReferral: (referralId: string) => ApiClient.delete(`/vertex/financing/referrals/${referralId}`),

  // ═══════════════════════════════════════════════════════════
  // PROPOSALBIO — Quality Analysis (10 Biohacks)
  // ═══════════════════════════════════════════════════════════
  analyzeProposalBio: (proposalId: string, metadata?: any) =>
    ApiClient.post('/gpss/proposalbio/analyze', { proposal_id: proposalId, metadata }),
  getProposalBioScore: (proposalId: string) =>
    ApiClient.get(`/gpss/proposalbio/score/${proposalId}`),
  approveProposal: (proposalId: string, approvedBy: string, overrideWarnings?: boolean) =>
    ApiClient.post('/gpss/proposalbio/approve', { proposal_id: proposalId, approved_by: approvedBy, override_warnings: overrideWarnings }),
  recordProposalOutcome: (proposalId: string, outcome: string, winValue?: number) =>
    ApiClient.post('/gpss/proposalbio/outcome', { proposal_id: proposalId, outcome, win_value: winValue }),

  // ═══════════════════════════════════════════════════════════
  // STRATEGIC ANALYSIS — Go/No-Go, Win Themes, Evaluator Profiles
  // ═══════════════════════════════════════════════════════════
  runGoNoGo: (opportunityId: string, data?: any) =>
    ApiClient.post('/gpss/strategic-analysis/go-no-go', { opportunity_id: opportunityId, ...data }),
  profileEvaluators: (opportunityId: string) =>
    ApiClient.post('/gpss/strategic-analysis/evaluator-profile', { opportunity_id: opportunityId }),
  getWinThemes: (opportunityId?: string) => {
    const params = opportunityId ? `?opportunity_id=${opportunityId}` : '';
    return ApiClient.get(`/gpss/strategic-analysis/win-themes${params}`);
  },
  selectWinThemes: (opportunityId: string, themeIds: string[]) =>
    ApiClient.post('/gpss/strategic-analysis/select-win-themes', { opportunity_id: opportunityId, theme_ids: themeIds }),
  getStrategicReport: (opportunityId: string) =>
    ApiClient.get(`/gpss/strategic-analysis/report/${opportunityId}`),

  // ═══════════════════════════════════════════════════════════
  // OFFICER OUTREACH — Capability Statement Distribution
  // ═══════════════════════════════════════════════════════════
  generateOutreachLetter: (data: any) =>
    ApiClient.post('/gpss/officer-outreach/generate', data),
  getOutreachLetters: () =>
    ApiClient.get('/gpss/officer-outreach/letters'),
  getOutreachLetter: (letterId: string) =>
    ApiClient.get(`/gpss/officer-outreach/letters/${letterId}`),
  updateOutreachLetter: (letterId: string, data: any) =>
    ApiClient.put(`/gpss/officer-outreach/letters/${letterId}`, data),
  getOutreachStats: () =>
    ApiClient.get('/gpss/officer-outreach/stats'),

  // ═══════════════════════════════════════════════════════════
  // AI RECOMMENDATIONS — Capability Gaps, Suppliers, Subcontractors
  // ═══════════════════════════════════════════════════════════
  getCapabilityGapRecommendations: (opportunityId: string) =>
    ApiClient.post('/ai/recommendations/capability-gap', { opportunity_id: opportunityId }),
  getSubcontractorRecommendations: (opportunityId: string) =>
    ApiClient.post('/ai/recommendations/subcontractors', { opportunity_id: opportunityId }),
  getSupplierRecommendations: (opportunityId: string) =>
    ApiClient.post('/ai/recommendations/suppliers', { opportunity_id: opportunityId }),
  approveRecommendation: (recommendationId: string) =>
    ApiClient.post(`/ai/recommendations/${recommendationId}/approve`, {}),
  getPendingRecommendations: () =>
    ApiClient.get('/ai/recommendations/pending'),

  // ═══════════════════════════════════════════════════════════
  // COMPLIANCE — Alerts, Checks, Subcontractor Compliance
  // ═══════════════════════════════════════════════════════════
  getComplianceAlerts: () =>
    ApiClient.get('/gpss/compliance/alerts'),
  calculateCompliance: (opportunityId: string) =>
    ApiClient.post('/ai/compliance/calculate', { opportunity_id: opportunityId }),
  checkSubcontractorCompliance: (subcontractorId: string) =>
    ApiClient.post(`/gpss/subcontractors/${subcontractorId}/compliance/check`, {}),

  // ═══════════════════════════════════════════════════════════
  // AUTO-QUOTE — Automated Quote Processing
  // ═══════════════════════════════════════════════════════════
  autoProcessOpportunity: (opportunityId: string) =>
    ApiClient.post('/gpss/auto-quote/process-opportunity', { opportunity_id: opportunityId }),
  autoFindSuppliers: (opportunityId: string) =>
    ApiClient.post('/gpss/auto-quote/find-suppliers', { opportunity_id: opportunityId }),
  getSupplierQuotes: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) Object.keys(filters).forEach(k => { if (filters[k]) params.append(k, filters[k]); });
    const query = params.toString();
    return ApiClient.get(`/gpss/supplier-quotes${query ? `?${query}` : ''}`);
  },
  updateSupplierQuote: (quoteId: string, data: any) =>
    ApiClient.put(`/gpss/supplier-quotes/${quoteId}`, data),

  // ═══════════════════════════════════════════════════════════
  // FULFILLMENT — Contract Delivery & Inventory
  // ═══════════════════════════════════════════════════════════
  getFulfillmentDashboard: () => ApiClient.get('/fulfillment/dashboard'),
  getFulfillmentContracts: () => ApiClient.get('/fulfillment/contracts'),
  createFulfillmentContract: (data: any) => ApiClient.post('/fulfillment/contracts', data),
  getFulfillmentDeliveries: (filters?: any) => {
    const params = new URLSearchParams();
    if (filters) Object.keys(filters).forEach(k => { if (filters[k]) params.append(k, filters[k]); });
    const query = params.toString();
    return ApiClient.get(`/fulfillment/deliveries${query ? `?${query}` : ''}`);
  },
  getInventory: () => ApiClient.get('/fulfillment/inventory'),
  getInventoryHealth: () => ApiClient.get('/fulfillment/inventory/health-check'),

  // ═══════════════════════════════════════════════════════════
  // CONTACTS — Auto-Extraction
  // ═══════════════════════════════════════════════════════════
  autoExtractContacts: (text: string, name: string) =>
    ApiClient.post('/api/contacts/auto-extract-solicitation', { text, name }),
  addSupplierContact: (data: any) =>
    ApiClient.post('/api/contacts/add-supplier', data),
  addSubcontractorContact: (data: any) =>
    ApiClient.post('/api/contacts/add-subcontractor', data),

  // ═══════════════════════════════════════════════════════════
  // CAPABILITY STATEMENTS
  // ═══════════════════════════════════════════════════════════
  getCapStatTemplates: () => ApiClient.get('/capability-statements/templates'),
  getCapStatList: () => ApiClient.get('/capability-statements/list'),
  generateCapStat: (data: any) => ApiClient.post('/capability-statements/generate', data),

  // ═══════════════════════════════════════════════════════════
  // FORECAST OUTREACH
  // ═══════════════════════════════════════════════════════════
  generateForecastOutreach: (forecastId: string) =>
    ApiClient.post(`/api/forecasts/${forecastId}/generate-capstat-outreach`, {}),
  batchForecastOutreach: (forecastIds: string[]) =>
    ApiClient.post('/api/forecasts/batch-outreach', { forecast_ids: forecastIds }),

  // ═══════════════════════════════════════════════════════════
  // NEXUS PIPELINE — Central Nervous System
  // ═══════════════════════════════════════════════════════════
  getPipelineHealth: () => ApiClient.get('/nexus/pipeline/health'),
  getPipelineContracts: (status?: string) => {
    const params = status ? `?status=${status}` : '';
    return ApiClient.get(`/nexus/pipeline/contracts${params}`);
  },
  getPipelineContract: (contractId: string) =>
    ApiClient.get(`/nexus/pipeline/contracts/${contractId}`),
  registerPipelineContract: (data: any) =>
    ApiClient.post('/nexus/pipeline/contracts', data),
  updatePipelineContract: (contractId: string, data: any) =>
    ApiClient.patch(`/nexus/pipeline/contracts/${contractId}`, data),
  firePipelineEvent: (data: any) =>
    ApiClient.post('/nexus/pipeline/event', data),
  getPipelineEvents: (limit?: number, contractId?: string) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', String(limit));
    if (contractId) params.append('contract_id', contractId);
    const query = params.toString();
    return ApiClient.get(`/nexus/pipeline/events${query ? `?${query}` : ''}`);
  },
  getPipelineTimeline: (contractId: string) =>
    ApiClient.get(`/nexus/pipeline/contracts/${contractId}/timeline`),
  dispatchPipelineOrders: (contractId: string, orders: any[]) =>
    ApiClient.post(`/nexus/pipeline/contracts/${contractId}/dispatch`, { orders }),
};
