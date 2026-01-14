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

  static async delete(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
    });
    return response.json();
  }
}

// API Functions
export const api = {
  // Health
  getHealth: () => ApiClient.get('/health'),

  // Dashboard
  getDashboardStats: () => ApiClient.get('/dashboard/stats'),
  getDashboardActivity: () => ApiClient.get('/dashboard/activity'),
  getDashboardAlerts: () => ApiClient.get('/dashboard/alerts'),

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
    source?: string;
    state?: string;
    edwsb_only?: boolean;
    urgency?: string;
    home_states_only?: boolean;
  }) => {
    const params = new URLSearchParams();
    if (filters?.source) params.append('source', filters.source);
    if (filters?.state) params.append('state', filters.state);
    if (filters?.edwsb_only) params.append('edwsb_only', 'true');
    if (filters?.urgency) params.append('urgency', filters.urgency);
    if (filters?.home_states_only) params.append('home_states_only', 'true');
    const query = params.toString();
    return ApiClient.get(`/gpss/opportunities${query ? `?${query}` : ''}`);
  },
  createGpssOpportunity: (data: any) => ApiClient.post('/gpss/opportunities', data),
  updateGpssOpportunity: (id: string, data: any) => ApiClient.put(`/gpss/opportunities/${id}`, data),
  getGpssStats: () => ApiClient.get('/gpss/stats'),
  
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
  minePortal: (portalId: string) =>
    ApiClient.post(`/gpss/mining/portal/${portalId}`, {}),
  autoMineAll: () =>
    ApiClient.post('/gpss/mining/auto-mine-all', {}),
  scrapeTarget: (targetId: string) =>
    ApiClient.post(`/gpss/mining/target/${targetId}`, {}),
  scrapeAllTargets: () =>
    ApiClient.post('/gpss/mining/scrape-all-targets', {}),
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

  // DDCSS Prospects API
  getDdcssProspects: () => ApiClient.get('/ddcss/prospects'),
  createDdcssProspect: (data: any) => ApiClient.post('/ddcss/prospects', data),

  // DDCSS Tools API
  getDdcssClientAvatars: () => ApiClient.get('/ddcss/client-avatars'),
  createDdcssClientAvatar: (data: any) => ApiClient.post('/ddcss/client-avatars', data),
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
};
