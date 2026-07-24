const LOCAL_API_DEFAULT = 'http://127.0.0.1:8000';
const PRODUCTION_API = 'https://deedavis.pythonanywhere.com';

const API_BASE = process.env.REACT_APP_API_BASE || LOCAL_API_DEFAULT;

/** Voice/Twilio/ElevenLabs — live on PA; local NEXUS UI defaults here unless overridden. */
export const VOICE_API_BASE =
  process.env.REACT_APP_VOICE_API_BASE ||
  (API_BASE !== LOCAL_API_DEFAULT ? API_BASE : PRODUCTION_API);

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

  static async getVoice(endpoint: string) {
    const response = await fetch(`${VOICE_API_BASE}${endpoint}`);
    return response.json();
  }

  static async postVoice(endpoint: string, data: any) {
    const response = await fetch(`${VOICE_API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
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

  /** SBA SubNet — subcontracting opportunities (scrape-backed; use modest max_pages). */
  searchSubnetOpportunities: (params?: {
    state?: string;
    keyword?: string;
    max_pages?: number;
    details?: boolean;
  }) => {
    const q = new URLSearchParams();
    if (params?.state) q.set('state', params.state);
    if (params?.keyword) q.set('keyword', params.keyword);
    if (params?.max_pages != null) q.set('max_pages', String(params.max_pages));
    if (params?.details) q.set('details', 'true');
    const qs = q.toString();
    return ApiClient.get(`/subnet/opportunities${qs ? `?${qs}` : ''}`);
  },
  syncSubnetToGpss: (body: {
    state?: string;
    keyword?: string;
    max_pages?: number;
    fetch_details?: boolean;
  }) => ApiClient.post('/subnet/sync', body || {}),

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
  getOpportunityDetails: (id: string) => ApiClient.get(`/gpss/opportunities/${id}/details`),
  generateCapabilityStatement: (opportunityId: string) => ApiClient.post(`/gpss/opportunities/${opportunityId}/generate-cap-statement`, {}),
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

  /** PRISM Voice Intake — NEMT call center (defaults to production PA for live Twilio/ElevenLabs) */
  getPrismVoiceStatus: () => ApiClient.getVoice('/prism/voice/status'),
  getPrismVoiceCalls: (limit = 50) => ApiClient.getVoice(`/prism/voice/calls?limit=${limit}`),
  simulatePrismVoiceCall: (data: { call_sid?: string; speech: string; caller?: string }) =>
    ApiClient.postVoice('/prism/voice/simulate', data),

  /** PRISM NEMT — trip dispatch, eligibility, complete → VERTEX invoice */
  getNemtOrderByPrism: (prismOrderId: string) =>
    ApiClient.get(`/prism/nemt/orders/by-prism/${encodeURIComponent(prismOrderId)}`),
  verifyNemtEligibility: (nemtOrderId: string, data?: Record<string, unknown>) =>
    ApiClient.post(`/prism/nemt/orders/${encodeURIComponent(nemtOrderId)}/verify-eligibility`, data || {}),
  dispatchNemtOrder: (nemtOrderId: string, data?: Record<string, unknown>) =>
    ApiClient.post(`/prism/nemt/orders/${encodeURIComponent(nemtOrderId)}/dispatch`, data || {}),
  setNemtRideTracking: (nemtOrderId: string, data: { rider_tracking_url: string; fulfillment_platform?: string }) =>
    ApiClient.post(`/prism/nemt/orders/${encodeURIComponent(nemtOrderId)}/ride-tracking`, data),
  completeNemtTrip: (nemtOrderId: string, data: Record<string, unknown>) =>
    ApiClient.post(`/prism/nemt/orders/${encodeURIComponent(nemtOrderId)}/complete`, data),
  getNemtEligibilityChecklist: (nemtOrderId: string) =>
    ApiClient.get(`/prism/nemt/orders/${encodeURIComponent(nemtOrderId)}/eligibility`),

  /** PRISM DOT: collector operator due-diligence brief (49 CFR Part 40 basics / audit risk) */
  getPrismDotCollectorDueDiligence: () => ApiClient.get('/prism/dot/collector-due-diligence'),

  /** PRISM Auto-QC: run automated compliance checks on demand */
  runPrismAutoQc: (orderId: string) => ApiClient.post(`/prism/orders/${orderId}/auto-qc`, {}),

  /** PRISM Document AI: full pipeline (signature, OCR, classify, seal, photo QC) */
  runPrismDocAiPipeline: (data: { images_b64: string[]; service_type: string; order_id?: string }) =>
    ApiClient.post('/prism/doc-ai/pipeline', data),
  getPrismDocAiSchemas: () => ApiClient.get('/prism/doc-ai/schemas'),
  detectPrismSignatures: (data: { image_b64: string; service_type: string }) =>
    ApiClient.post('/prism/doc-ai/detect-signatures', data),
  extractPrismFormFields: (data: { image_b64: string; form_type: string }) =>
    ApiClient.post('/prism/doc-ai/extract-fields', data),
  classifyPrismPage: (data: { image_b64: string }) =>
    ApiClient.post('/prism/doc-ai/classify-page', data),

  /** PRISM QC Learning: risk scoring + agent profiling */
  getPrismRiskScore: (data: { order_id: string }) =>
    ApiClient.post('/prism/qc-learning/risk-score', data),
  trainPrismRiskModel: () => ApiClient.post('/prism/qc-learning/train', {}),
  getPrismAgentProfile: (agentName: string) =>
    ApiClient.get(`/prism/qc-learning/agent-profile/${encodeURIComponent(agentName)}`),
  getPrismAgentProfiles: () => ApiClient.get('/prism/qc-learning/agent-profiles'),
  getPrismAgentsActionNeeded: () => ApiClient.get('/prism/qc-learning/agents-action-needed'),
  recordPrismQcOutcome: (data: { agent_name: string; order_id: string; service_type: string; outcome: string; errors?: any[] }) =>
    ApiClient.post('/prism/qc-learning/record-outcome', data),
  rebuildPrismAgentProfiles: () => ApiClient.post('/prism/qc-learning/rebuild-profiles', {}),
  getPrismRiskModelWeights: () => ApiClient.get('/prism/qc-learning/model-weights'),

  /** PRISM Router: credential check */
  checkPrismAgentCredentials: (data: { agent: any; service_type: string }) =>
    ApiClient.post('/prism/router/credential-check', data),

  /** PRISM Router: sub/agent credentialing fee catalog (NALI / Quest / bundles) */
  getPrismCredentialingPricing: () => ApiClient.get('/prism/router/credentialing-pricing'),

  /** PRISM Router: quote DDI credentialing fees — body: { full_package } | { bundles: string[] } | { credentials: string[] } */
  postPrismCredentialingQuote: (data: { full_package?: string; bundles?: string[]; credentials?: string[] }) =>
    ApiClient.post('/prism/router/credentialing-quote', data),

  /** PRISM Signature Reference Map — Phase A (reference doc from escrow/title/lender) */
  createOrderSignatureMap: (
    orderId: string,
    data: { images_b64: string[]; document_type?: string; document_context?: string }
  ) => ApiClient.post(`/prism/orders/${orderId}/signature-map`, data),
  getOrderSignatureMap: (orderId: string) =>
    ApiClient.get(`/prism/orders/${orderId}/signature-map`),

  /** PRISM Signature Verification — Phase B (verify completed scanback against map) */
  verifyOrderSignatures: (data: { order_id: string; images_b64: string[] }) =>
    ApiClient.post('/prism/doc-ai/verify-signatures', data),
  getSignatureVerificationResult: (orderId: string) =>
    ApiClient.get(`/prism/doc-ai/verification-result/${orderId}`),

  /** PRISM Signature Map — direct doc-ai endpoints */
  mapDocumentSignatures: (data: {
    order_id: string;
    images_b64: string[];
    document_type?: string;
    document_context?: string;
  }) => ApiClient.post('/prism/doc-ai/map-signatures', data),
  deleteOrderSignatureMap: (orderId: string) =>
    ApiClient.delete(`/prism/doc-ai/signature-map/${orderId}`),
  getSignerTypes: () => ApiClient.get('/prism/doc-ai/signer-types'),

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

  /** DDCSS email templates — HTML from disk, company_info placeholders */
  getEmailTemplateCategories: () => ApiClient.get('/email-templates/categories'),
  generateEmailTemplate: (data: {
    category?: string;
    variant?: string;
    recipientFirstName?: string;
    planDisplayName?: string;
    customParagraph?: string;
    outputDir?: string;
    extraReplacements?: Record<string, string>;
  }) => ApiClient.post('/email-templates/generate', data),

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

  // VERTEX Financial System
  createVertexInvoice: (data: any) => ApiClient.post('/vertex/invoices', data),
  updateVertexInvoice: (invoiceId: string, data: any) => ApiClient.put(`/vertex/invoices/${invoiceId}`, data),
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

  // VERTEX NEMT Medical Billing (HAP CareSource / CHAMPS)
  vertexNemtLogTrip: (data: any) => ApiClient.post('/vertex/nemt/log-trip', data),
  vertexNemtGenerateClaim: (data: any) => ApiClient.post('/vertex/nemt/generate-claim', data),
  vertexNemtPendingClaims: () => ApiClient.get('/vertex/nemt/pending-claims'),
  vertexNemtPostPayment: (data: any) => ApiClient.post('/vertex/nemt/post-payment', data),
  vertexNemtGetRates: () => ApiClient.get('/vertex/nemt/rates'),
  vertexNemtUpdateRate: (recordId: string, data: any) =>
    ApiClient.put(`/vertex/nemt/rates/${encodeURIComponent(recordId)}`, data),
  vertexNemtSeedRates: () => ApiClient.post('/vertex/nemt/rates/seed', {}),
  vertexNemtInvoicePdfUrl: (invoiceId: string) =>
    `${API_BASE}/vertex/nemt/invoice/${encodeURIComponent(invoiceId)}/pdf`,

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
  // COMPASS — Post-Award Contract Management
  // ═══════════════════════════════════════════════════════════
  getCompassStats: () => ApiClient.get('/compass/stats'),
  getCompassContracts: () => ApiClient.get('/compass/contracts'),
  getCompassContract: (contractId: string) => ApiClient.get(`/compass/contracts/${contractId}`),
  createCompassContract: (data: any) => ApiClient.post('/compass/contracts', data),
  updateCompassContract: (contractId: string, data: any) => ApiClient.put(`/compass/contracts/${contractId}`, data),
  getCompassContractHealth: (contractId: string) => ApiClient.get(`/compass/contracts/${contractId}/health`),
  generatePerformanceReport: (contractId: string) => ApiClient.post(`/compass/contracts/${contractId}/performance-report`, {}),
  createCompassDeliverable: (data: any) => ApiClient.post('/compass/deliverables', data),
  updateCompassDeliverable: (deliverableId: string, data: any) => ApiClient.put(`/compass/deliverables/${deliverableId}`, data),
  createCompassCommunication: (data: any) => ApiClient.post('/compass/communications', data),
  getCompassCommunications: (contractId: string) => ApiClient.get(`/compass/communications/${contractId}`),
  createCompassModification: (data: any) => ApiClient.post('/compass/modifications', data),

  // ═══════════════════════════════════════════════════════════
  // NEXUS PIPELINE — Central Nervous System
  // ═══════════════════════════════════════════════════════════
  getPipelineHealth: () => ApiClient.get('/nexus/pipeline/health'),
  getNexusContracts: () => ApiClient.get('/nexus/vault'),
  getNexusContract: (contractId: string) => ApiClient.get(`/nexus/vault/${contractId}`),
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

  // ═══════════════════════════════════════════════════════════
  // JETA — Aviation fuel buyers (Airtable JETA_Buyers)
  // ═══════════════════════════════════════════════════════════
  getJetaBuyers: (filters?: {
    state?: string;
    buyer_type?: string;
    pipeline_stage?: string;
    supplier_status?: string;
    /** Minimum priority score 0–130 (e.g. 60 for top prospects) */
    min_priority_score?: string | number;
  }) => {
    const params = new URLSearchParams();
    if (filters?.state) params.set('state', filters.state);
    if (filters?.buyer_type) params.set('buyer_type', filters.buyer_type);
    if (filters?.pipeline_stage) params.set('pipeline_stage', filters.pipeline_stage);
    if (filters?.supplier_status) params.set('supplier_status', filters.supplier_status);
    if (filters?.min_priority_score != null && filters.min_priority_score !== '')
      params.set('min_priority_score', String(filters.min_priority_score));
    const q = params.toString();
    return ApiClient.get(`/jeta/buyers${q ? `?${q}` : ''}`);
  },
  createJetaBuyer: (data: Record<string, unknown>) => ApiClient.post('/jeta/buyers', data),
  updateJetaBuyer: (buyerId: string, data: Record<string, unknown>) =>
    ApiClient.put(`/jeta/buyers/${buyerId}`, data),

  /** Create JETA_Sellers row from buyer (supply_adjacent + Open supplier). */
  postJetaSellerFromBuyer: (buyerId: string) =>
    ApiClient.post('/jeta/sellers/from-buyer', { buyer_id: buyerId }),

  /** Multipart CSV upload — FAA 5010 → JETA_Buyers (all states). */
  postJetaImportFaa: async (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    const response = await fetch(`${API_BASE}/jeta/import/faa`, {
      method: 'POST',
      body: fd,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return {
        success: false,
        error: (data as { error?: string }).error || `HTTP ${response.status}`,
        ...data,
      };
    }
    return data;
  },

  /** Multipart CSV upload — Transport Canada / NAV CANADA → JETA_Buyers. */
  postJetaImportCanada: async (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    const response = await fetch(`${API_BASE}/jeta/import/canada`, {
      method: 'POST',
      body: fd,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return {
        success: false,
        error: (data as { error?: string }).error || `HTTP ${response.status}`,
        ...data,
      };
    }
    return data;
  },

  getJetaOutreachDueBuyers: () => ApiClient.get('/jeta/outreach/due-buyers'),
  getJetaOutreach: (filters?: {
    channel?: string;
    response_status?: string;
    sort?: 'touch_date_desc' | 'touch_date_asc';
  }) => {
    const params = new URLSearchParams();
    if (filters?.channel) params.set('channel', filters.channel);
    if (filters?.response_status) params.set('response_status', filters.response_status);
    if (filters?.sort) params.set('sort', filters.sort);
    const q = params.toString();
    return ApiClient.get(`/jeta/outreach${q ? `?${q}` : ''}`);
  },
  createJetaOutreach: (data: Record<string, unknown>) => ApiClient.post('/jeta/outreach', data),

  /** Claude draft for JETA outreach email (Outreach Center). */
  postJetaOutreachAiDraft: (data: {
    buyerId?: string;
    touchNumber: number;
    contactName?: string;
    companyName?: string;
    buyerType?: string;
    airport?: string;
    state?: string;
  }) => ApiClient.post('/jeta/outreach/ai-draft', data),

  /** AI drafts escalation / market notices for active deals (Dashboard — counterparty notices). */
  postJetaEscalationNoticeDraft: (data?: { dealIds?: string[] }) =>
    ApiClient.post('/jeta/notifications/escalation-notice-draft', data ?? {}),

  getJetaDeals: (filters?: { deal_stage?: string; integrity?: boolean }) => {
    const params = new URLSearchParams();
    if (filters?.deal_stage) params.set('deal_stage', filters.deal_stage);
    if (filters?.integrity) params.set('integrity', '1');
    const q = params.toString();
    return ApiClient.get(`/jeta/deals${q ? `?${q}` : ''}`);
  },
  getJetaFraudDashboardAlerts: () => ApiClient.get('/jeta/fraud/dashboard-alerts'),
  getJetaFraudGateCatalog: () => ApiClient.get('/jeta/fraud/gate-catalog'),
  /** Master doc TABLE 11 — JETA_FraudLog (flagged_record_type, links, blacklisted, etc.). */
  getJetaFraudLog: (filters?: {
    flagged_record_type?: string;
    flagged_record_id?: string;
    record_type?: string;
    company_name?: string;
    blacklisted?: string;
  }) => {
    const p = new URLSearchParams();
    if (filters?.flagged_record_type) p.set('flagged_record_type', filters.flagged_record_type);
    if (filters?.flagged_record_id) p.set('flagged_record_id', filters.flagged_record_id);
    if (filters?.record_type) p.set('record_type', filters.record_type);
    if (filters?.company_name) p.set('company_name', filters.company_name);
    if (filters?.blacklisted) p.set('blacklisted', filters.blacklisted);
    const q = p.toString();
    return ApiClient.get(`/jeta/fraud-log${q ? `?${q}` : ''}`);
  },
  createJetaFraudLog: (data: Record<string, unknown>) => ApiClient.post('/jeta/fraud-log', data),
  updateJetaFraudLog: (id: string, data: Record<string, unknown>) => ApiClient.patch(`/jeta/fraud-log/${id}`, data),
  /** Master doc — JETA_ImportLog (FAA 5010 / Canada batch audits). */
  getJetaImportLog: (filters?: { import_source?: string; file_name?: string; imported_by?: string }) => {
    const p = new URLSearchParams();
    if (filters?.import_source) p.set('import_source', filters.import_source);
    if (filters?.file_name) p.set('file_name', filters.file_name);
    if (filters?.imported_by) p.set('imported_by', filters.imported_by);
    const q = p.toString();
    return ApiClient.get(`/jeta/import-log${q ? `?${q}` : ''}`);
  },
  createJetaImportLog: (data: Record<string, unknown>) => ApiClient.post('/jeta/import-log', data),
  updateJetaImportLog: (id: string, data: Record<string, unknown>) => ApiClient.patch(`/jeta/import-log/${id}`, data),
  /** Master doc TABLE 12 — JETA_Events. */
  getJetaEvents: (filters?: { attending?: string; event_type?: string; q?: string }) => {
    const p = new URLSearchParams();
    if (filters?.attending) p.set('attending', filters.attending);
    if (filters?.event_type) p.set('event_type', filters.event_type);
    if (filters?.q) p.set('q', filters.q);
    const qs = p.toString();
    return ApiClient.get(`/jeta/events${qs ? `?${qs}` : ''}`);
  },
  createJetaEvent: (data: Record<string, unknown>) => ApiClient.post('/jeta/events', data),
  updateJetaEvent: (id: string, data: Record<string, unknown>) => ApiClient.patch(`/jeta/events/${id}`, data),
  /** JETA market: latest IATA jet fuel $/bbl from Airtable; use refresh=true to fetch IATA and store. */
  getJetaMarketPrice: (opts?: { refresh?: boolean }) => {
    const params = new URLSearchParams();
    if (opts?.refresh) params.set('refresh', '1');
    const q = params.toString();
    return ApiClient.get(`/jeta/market/price${q ? `?${q}` : ''}`);
  },
  /** ICAO airport fuel supplier reference; persists rows to JETA_SupplierDirectory. */
  getJetaSuppliersLookup: (icao: string) =>
    ApiClient.get(`/jeta/suppliers/lookup?icao=${encodeURIComponent(icao)}`),
  createJetaDeal: (data: Record<string, unknown>) => ApiClient.post('/jeta/deals', data),
  updateJetaDeal: (dealId: string, data: Record<string, unknown>) =>
    ApiClient.put(`/jeta/deals/${dealId}`, data),

  getJetaDocuments: () => ApiClient.get('/jeta/documents'),
  postJetaDocumentsGenerate: (data: { dealId: string; documentType: string }) =>
    ApiClient.post('/jeta/documents/generate', data),

  // ═══════════════════════════════════════════════════════════
  // SHIELD — Lead Screening & MDHHS Referral Module
  // Michigan PA 146 of 2023 — universal blood lead screening mandate
  // ═══════════════════════════════════════════════════════════
  getShieldDashboard: () => ApiClient.get('/shield/dashboard'),
  getShieldReferrals: (filters?: {
    status?: string;
    county?: string;
    urgency?: string;
    referral_source?: string;
  }) => {
    const p = new URLSearchParams();
    if (filters?.status) p.set('status', filters.status);
    if (filters?.county) p.set('county', filters.county);
    if (filters?.urgency) p.set('urgency', filters.urgency);
    if (filters?.referral_source) p.set('referral_source', filters.referral_source);
    const q = p.toString();
    return ApiClient.get(`/shield/referrals${q ? `?${q}` : ''}`);
  },
  getShieldReferral: (referralId: string) =>
    ApiClient.get(`/shield/referrals/${encodeURIComponent(referralId)}`),
  createShieldReferral: (data: Record<string, unknown>) =>
    ApiClient.post('/shield/referrals', data),
  updateShieldReferral: (referralId: string, data: Record<string, unknown>) =>
    ApiClient.patch(`/shield/referrals/${encodeURIComponent(referralId)}`, data),

  getShieldFamilies: () => ApiClient.get('/shield/families'),
  getShieldChildren: () => ApiClient.get('/shield/children'),
  getShieldNavigators: () => ApiClient.get('/shield/navigators'),

  getShieldActivations: (referralId?: string) => {
    const q = referralId ? `?referral_id=${encodeURIComponent(referralId)}` : '';
    return ApiClient.get(`/shield/activations${q}`);
  },
  activateShieldService: (data: {
    referral_id: string;
    family_id?: string;
    service_line: string;
    vendor?: string;
    authorization_number?: string;
    appointment_date?: string;
    notes?: string;
    status?: string;
    navigator_name?: string;
    displacement_required?: boolean;
  }) => ApiClient.post('/shield/activations', data),

  logShieldMilestone: (data: {
    referral_id?: string;
    family_id?: string;
    milestone_type: string;
    recorded_by?: string;
    notes?: string;
  }) => ApiClient.post('/shield/milestones', data),

  getShieldBilling: (status?: string) => {
    const q = status ? `?status=${encodeURIComponent(status)}` : '';
    return ApiClient.get(`/shield/billing${q}`);
  },
  createShieldBilling: (data: Record<string, unknown>) =>
    ApiClient.post('/shield/billing', data),
  approveShieldBilling: (recordId: string, data: { supervisor_email: string; supervisor_name: string; vertex_invoice_id?: string }) =>
    ApiClient.post(`/shield/billing/${recordId}/approve`, data),

  getShieldOutcomesReport: (period?: string, county?: string) => {
    const p = new URLSearchParams();
    if (period) p.set('period', period);
    if (county) p.set('county', county);
    const q = p.toString();
    return ApiClient.get(`/shield/outcomes-report${q ? `?${q}` : ''}`);
  },

  shieldAiChat: (message: string, context?: Record<string, unknown>) =>
    ApiClient.post('/shield/ai/chat', { message, context }),
  shieldAiExternal: (data: { message: string; case_ref?: string; agency_email: string }) =>
    ApiClient.post('/shield/ai/external', data),

  // SLA override — supervisor / admin only; backend enforces via Navigators.role.
  // Pass target_hours = null (or 0) to CLEAR an existing override.
  overrideShieldSLA: (
    referralId: string,
    data: { user_email: string; target_hours: number | null; reason?: string },
  ) =>
    ApiClient.post(
      `/shield/referrals/${encodeURIComponent(referralId)}/sla-override`,
      data,
    ),

  // Update a child record (triggers BLL auto-escalation server-side)
  updateShieldChild: (childId: string, data: Record<string, unknown>) =>
    ApiClient.patch(`/shield/children/${encodeURIComponent(childId)}`, data),

  // Public: family status lookup by case number + last name
  shieldFamilyLookup: (caseNumber: string, lastName: string) =>
    ApiClient.post('/shield/family-status', { case_number: caseNumber, last_name: lastName }),

  // Notification channels status (SMS/email enabled?)
  getShieldNotificationStatus: () => ApiClient.get('/shield/notifications/status'),

  // Notification log for a referral
  getShieldNotificationLog: (referralId?: string) => {
    const q = referralId ? `?referral_id=${encodeURIComponent(referralId)}` : '';
    return ApiClient.get(`/shield/notifications/log${q}`);
  },

  // Call log — navigator phone system
  getShieldCallLog: (navigatorEmail?: string) => {
    const q = navigatorEmail ? `?navigator=${encodeURIComponent(navigatorEmail)}` : '';
    return ApiClient.get(`/shield/calls${q}`);
  },
  logShieldCall: (data: {
    referral_id?: string;
    phone: string;
    direction: 'outbound' | 'inbound';
    duration_sec: number;
    notes?: string;
    navigator_email: string;
    navigator_name?: string;
    status: string;
  }) => ApiClient.post('/shield/calls', data),

  // Twilio click-to-call — initiates outbound call through backend
  shieldInitiateCall: (data: {
    to: string;
    navigator_phone: string;
    referral_id?: string;
    navigator_email: string;
  }) => ApiClient.post('/shield/calls/initiate', data),

  // SMS — send text to family from navigator
  shieldSendSMS: (data: {
    to: string;
    message: string;
    referral_id?: string;
    navigator_email: string;
  }) => ApiClient.post('/shield/sms/send', data),

  // Activity log — navigator time tracking
  logShieldActivity: (data: {
    referral_id: string;
    activity_type: string;
    duration_minutes: number;
    note?: string;
    navigator_email: string;
  }) => ApiClient.post('/shield/activity-log', data),

  getShieldActivityLog: (navigatorEmail?: string) => {
    const q = navigatorEmail ? `?navigator_email=${encodeURIComponent(navigatorEmail)}` : '';
    return ApiClient.get(`/shield/activity-log${q}`);
  },

  // Document upload stub
  shieldUploadDocument: (data: Record<string, unknown>) =>
    ApiClient.post('/shield/documents/upload', data),

  // Navigator login — verify against Navigators table
  shieldNavigatorLogin: (data: { email: string; name: string }) =>
    ApiClient.post('/shield/navigator/login', data),

  // SHIELD Contractors
  getShieldContractors: () => ApiClient.get('/shield/contractors'),
  createShieldContractor: (data: Record<string, unknown>) =>
    ApiClient.post('/shield/contractors', data),

  // SHIELD Outcomes Reporting
  getShieldOutcomes: () => ApiClient.get('/shield/outcomes'),
  createShieldOutcome: (data: Record<string, unknown>) =>
    ApiClient.post('/shield/outcomes', data),

  // Service Verification Engine
  getVerificationStatus: (activationId: string) =>
    ApiClient.get(`/shield/verification/${encodeURIComponent(activationId)}`),

  completeVerificationStep: (activationId: string, data: {
    step_key: string;
    verified_by: string;
    evidence?: string;
  }) => ApiClient.post(`/shield/verification/${encodeURIComponent(activationId)}/complete`, data),

  sendVerificationRequest: (activationId: string, stepKey: string) =>
    ApiClient.post(`/shield/verification/${encodeURIComponent(activationId)}/send-request`, { step_key: stepKey }),

  getOverdueVerifications: () =>
    ApiClient.get('/shield/verification/overdue'),

  getVerificationWorkflow: (serviceLine: string) =>
    ApiClient.get(`/shield/verification/workflow/${encodeURIComponent(serviceLine)}`),

  // ═══════════════════════════════════════════════════════════
  // HAVEN — Disaster Response TPA
  // Housing · Assistance · Vital Emergency Network
  // ═══════════════════════════════════════════════════════════
  getHavenStatus: () => ApiClient.get('/haven/status'),
  getHavenReadiness: () => ApiClient.get('/haven/readiness'),
  getHavenNetworkStats: () => ApiClient.get('/haven/network'),
  getHavenTransportPartners: (state?: string) => {
    const q = state ? `?state=${state}` : '';
    return ApiClient.get(`/haven/partners/transport${q}`);
  },
  getHavenHousingPartners: (state?: string) => {
    const q = state ? `?state=${state}` : '';
    return ApiClient.get(`/haven/partners/housing${q}`);
  },
  getHavenMedicalPartners: (state?: string) => {
    const q = state ? `?state=${state}` : '';
    return ApiClient.get(`/haven/partners/medical${q}`);
  },
  updateHavenPartner: (table: string, recordId: string, data: Record<string, unknown>) =>
    ApiClient.patch(`/haven/partners/${table}/${recordId}`, data),
  getHavenMCOs: (state?: string) => {
    const q = state ? `?state=${state}` : '';
    return ApiClient.get(`/haven/mcos${q}`);
  },
  updateHavenMCO: (recordId: string, data: Record<string, unknown>) =>
    ApiClient.patch(`/haven/mcos/${recordId}`, data),
  getHavenMCOPipeline: () => ApiClient.get('/haven/mcos/pipeline'),
  createHavenEvent: (data: Record<string, unknown>) =>
    ApiClient.post('/haven/events', data),
  getHavenEvents: () => ApiClient.get('/haven/events'),
  createHavenCase: (data: Record<string, unknown>) =>
    ApiClient.post('/haven/cases', data),
  getHavenCases: () => ApiClient.get('/haven/cases'),

  // HAVEN Disaster Watch — FEMA + NWS live monitoring
  getHavenWatchFeed: () => ApiClient.get('/haven/watch/feed'),
  getHavenThreatAssessment: () => ApiClient.get('/haven/watch/threat'),
  getHavenFemaDisasters: (days?: number) => {
    const q = days ? `?days=${days}` : '';
    return ApiClient.get(`/haven/watch/fema${q}`);
  },
  getHavenNwsAlerts: () => ApiClient.get('/haven/watch/nws'),

  // HAVEN Outreach Engine — automated partner/MCO onboarding
  generateHavenOutreach: (partnerType: string, partner: Record<string, unknown>) =>
    ApiClient.post('/haven/outreach/generate', { partner_type: partnerType, partner }),
  generateHavenFollowup: (partnerType: string, partner: Record<string, unknown>, daysSince?: number) =>
    ApiClient.post('/haven/outreach/followup', { partner_type: partnerType, partner, days_since: daysSince || 7 }),
  generateHavenNDA: (partnerType: string, partner: Record<string, unknown>) =>
    ApiClient.post('/haven/outreach/nda', { partner_type: partnerType, partner }),
  generateHavenAgreement: (partnerType: string, partner: Record<string, unknown>) =>
    ApiClient.post('/haven/outreach/agreement', { partner_type: partnerType, partner }),
  getHavenPipelineActions: (partner: Record<string, unknown>) =>
    ApiClient.post('/haven/outreach/actions', { partner }),
};
