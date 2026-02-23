import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface Lead {
  id: string;
  fields: {
    'Lead ID'?: string;
    'Client Name': string;
    'Property Address': string;
    'City': string;
    'County': string;
    'State': string;
    'Surplus Amount': number;
    'Your Fee (30%)': number;
    'Client Portion (70%)': number;
    'Status': string;
    'Lead Stage': string;
    'Priority Score': number;
    'Win Probability': number;
    'Contact Phone'?: string;
    'Contact Email'?: string;
    'Date Discovered'?: string;
    'Last Contact Date'?: string;
    'Next Follow-up Date'?: string;
  };
}

interface Task {
  id: string;
  fields: {
    'Task Title': string;
    'Task Description'?: string;
    'Task Type': string;
    'Priority': string;
    'Status': string;
    'Due Date': string;
    'Assigned To'?: string;
  };
}

interface Document {
  id: string;
  fields: {
    'Document Name': string;
    'Document Type': string;
    'Generated Content': string;
    'Status': string;
    'Generated Date': string;
    'AI Enhanced'?: boolean;
  };
}

interface Analytics {
  total_leads: number;
  total_surplus: number;
  total_fees: number;
  tasks_today: number;
  contracts_signed: number;
  leads_by_state: { [key: string]: number };
  leads_by_status: { [key: string]: number };
  average_surplus: number;
}

type TabType = 'dashboard' | 'leads' | 'documents' | 'tasks' | 'mining' | 'analytics';

export const LBPCSystem: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [leads, setLeads] = useState<Lead[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [documentPreview, setDocumentPreview] = useState<string | null>(null);
  const [showRocketLawyerModal, setShowRocketLawyerModal] = useState(false);
  const [rocketLawyerInstructions, setRocketLawyerInstructions] = useState<{docType: string; content: string} | null>(null);
  const [miningCounty, setMiningCounty] = useState('');
  const [miningState, setMiningState] = useState('');
  const [miningInProgress, setMiningInProgress] = useState(false);
  
  // Filters
  const [stateFilter, setStateFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard' || activeTab === 'analytics') {
        const analyticsRes = await fetch('/lbpc/analytics');
        const analyticsData = await analyticsRes.json();
        if (analyticsData.success) {
          setAnalytics(analyticsData.analytics);
        }
      }
      
      if (activeTab === 'leads' || activeTab === 'dashboard') {
        const leadsRes = await fetch('/lbpc/leads');
        const leadsData = await leadsRes.json();
        if (leadsData.success) {
          setLeads(leadsData.leads);
        }
      }
      
      if (activeTab === 'tasks') {
        const tasksRes = await fetch('/lbpc/tasks?status=Pending,In Progress');
        const tasksData = await tasksRes.json();
        if (tasksData.success) {
          setTasks(tasksData.tasks);
        }
      }
      
      if (activeTab === 'documents') {
        const docsRes = await fetch('/lbpc/documents');
        const docsData = await docsRes.json();
        if (docsData.success) {
          setDocuments(docsData.documents);
        }
      }
    } catch (error) {
      console.error('Error loading LBPC data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDocument = async (leadId: string, templateType: string) => {
    try {
      const response = await fetch(`/lbpc/leads/${leadId}/generate-document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template_type: templateType, use_ai: true })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setDocumentPreview(data.document_text);
        alert('Document generated successfully!');
        loadData();
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert(`Error generating document: ${error}`);
    }
  };

  // Rocket Lawyer Integration Functions
  const handleGenerateForRocketLawyer = async (leadId: string, templateType: string) => {
    try {
      const response = await fetch(`/lbpc/leads/${leadId}/generate-document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template_type: templateType, use_ai: true })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Copy to clipboard
        await navigator.clipboard.writeText(data.document_text);
        
        // Show Rocket Lawyer instructions
        setRocketLawyerInstructions({
          docType: templateType,
          content: data.document_text
        });
        setShowRocketLawyerModal(true);
        
        // Auto-open Rocket Lawyer in new tab
        window.open('https://www.rocketlawyer.com/dashboard', '_blank');
        
        // Update lead status if needed
        const currentLead = leads.find(l => l.id === leadId);
        if (templateType === 'Engagement Agreement' && currentLead?.fields.Status !== 'Document Sent') {
          await handleUpdateLeadStatus(leadId, 'Document Sent');
        }
        
        loadData();
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert(`Error generating document: ${error}`);
    }
  };

  const handleMarkSentForSignature = async (leadId: string) => {
    try {
      const response = await fetch(`/lbpc/leads/${leadId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          Status: 'Document Sent',
          'Last Contact Date': new Date().toISOString().split('T')[0]
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert('✅ Lead marked as "Document Sent for Signature"');
        loadData();
      }
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  const handleUpdateLeadStatus = async (leadId: string, newStatus: string) => {
    try {
      const response = await fetch(`/lbpc/leads/${leadId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ Status: newStatus })
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadData();
        alert('Status updated successfully!');
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert(`Error updating status: ${error}`);
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      const response = await fetch(`/lbpc/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ Status: 'Completed', 'Completed Date': new Date().toISOString() })
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadData();
        alert('Task completed!');
      }
    } catch (error) {
      alert(`Error completing task: ${error}`);
    }
  };

  const handleImportCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target?.result as string;
      const rows = text.split('\n').map(row => row.split(','));
      const headers = rows[0];
      const leads = rows.slice(1).map(row => {
        const lead: any = {};
        headers.forEach((header, index) => {
          lead[header.trim().toLowerCase()] = row[index]?.trim();
        });
        return lead;
      });

      try {
        const response = await fetch('/lbpc/import-csv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ leads })
        });

        const data = await response.json();
        if (data.success) {
          alert(`Imported ${data.imported} leads! (${data.skipped} skipped as duplicates)`);
          loadData();
        }
      } catch (error) {
        alert(`Error importing CSV: ${error}`);
      }
    };
    reader.readAsText(file);
  };

  const handleUploadPDF = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!miningCounty || !miningState) {
      alert('Please select county and state first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('county', miningCounty);
    formData.append('state', miningState);

    setMiningInProgress(true);
    try {
      const response = await fetch('/lbpc/upload-pdf', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        alert(`✅ PDF Processed!\nImported: ${data.imported} leads\nSkipped: ${data.skipped} duplicates`);
        loadData();
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert(`Error uploading PDF: ${error}`);
    } finally {
      setMiningInProgress(false);
    }
  };

  const handleUploadCountyCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!miningCounty || !miningState) {
      alert('Please select county and state first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('county', miningCounty);
    formData.append('state', miningState);

    setMiningInProgress(true);
    try {
      const response = await fetch('/lbpc/upload-csv', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        alert(`✅ CSV Processed!\nImported: ${data.imported} leads\nSkipped: ${data.skipped} duplicates`);
        loadData();
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert(`Error uploading CSV: ${error}`);
    } finally {
      setMiningInProgress(false);
    }
  };

  const handleMineCounty = async (county: string, state: string) => {
    setMiningInProgress(true);
    try {
      const response = await fetch('/lbpc/mine/county', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ county, state })
      });

      const data = await response.json();
      if (data.success) {
        alert(`✅ Mining Complete!\n${data.message}\nImported: ${data.imported} leads`);
        loadData();
      } else {
        alert(`Mining Note: ${data.error}\n\nTip: Use PDF/CSV upload for this county instead.`);
      }
    } catch (error) {
      alert(`Error mining county: ${error}`);
    } finally {
      setMiningInProgress(false);
    }
  };

  const filteredLeads = leads.filter(lead => {
    if (stateFilter && lead.fields.State !== stateFilter) return false;
    if (statusFilter && lead.fields.Status !== statusFilter) return false;
    if (searchQuery) {
      const searchLower = searchQuery.toLowerCase();
      const searchableText = `${lead.fields['Client Name']} ${lead.fields['Property Address']} ${lead.fields.County}`.toLowerCase();
      if (!searchableText.includes(searchLower)) return false;
    }
    return true;
  });

  // Dashboard Tab
  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="text-gray-400 text-sm font-medium">Total Leads</div>
          <div className="text-3xl font-bold text-white mt-2">{analytics?.total_leads || 0}</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="text-gray-400 text-sm font-medium">Total Surplus</div>
          <div className="text-3xl font-bold text-green-400 mt-2">
            ${(analytics?.total_surplus || 0).toLocaleString()}
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="text-gray-400 text-sm font-medium">Your Potential Fees (30%)</div>
          <div className="text-3xl font-bold text-purple-400 mt-2">
            ${(analytics?.total_fees || 0).toLocaleString()}
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-orange-500">
          <div className="text-gray-400 text-sm font-medium">Tasks Due Today</div>
          <div className="text-3xl font-bold text-orange-400 mt-2">{analytics?.tasks_today || 0}</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-indigo-500">
          <div className="text-gray-400 text-sm font-medium">Contracts Signed</div>
          <div className="text-3xl font-bold text-indigo-400 mt-2">{analytics?.contracts_signed || 0}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Leads</h3>
          <div className="space-y-3">
            {leads.slice(0, 5).map(lead => (
              <div key={lead.id} className="flex items-center justify-between p-3 bg-gray-900 rounded hover:bg-gray-700">
                <div>
                  <div className="font-medium">{lead.fields['Client Name']}</div>
                  <div className="text-sm text-gray-400">
                    {lead.fields.County}, {lead.fields.State} • ${lead.fields['Surplus Amount'].toLocaleString()}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  lead.fields.Status === 'New' ? 'bg-blue-500/20 text-blue-300' :
                  lead.fields.Status === 'Contacted' ? 'bg-yellow-500/20 text-yellow-300' :
                  lead.fields.Status === 'Contract Signed' ? 'bg-green-500/20 text-green-300' :
                  'bg-gray-700 text-gray-200'
                }`}>
                  {lead.fields.Status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Leads by State</h3>
          <div className="space-y-2">
            {Object.entries(analytics?.leads_by_state || {}).slice(0, 6).map(([state, count]) => (
              <div key={state} className="flex items-center justify-between">
                <span className="text-gray-300">{state}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-blue-500/100 h-2 rounded-full"
                      style={{ width: `${(count / (analytics?.total_leads || 1)) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-white w-8">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Leads Tab
  const renderLeads = () => (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <input
          type="text"
          placeholder="Search leads..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 min-w-[200px] px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
        />
        <select
          value={stateFilter}
          onChange={(e) => setStateFilter(e.target.value)}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
        >
          <option value="">All States</option>
          {['MI', 'GA', 'MD', 'TX', 'CA', 'IL'].map(state => (
            <option key={state} value={state}>{state}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
        >
          <option value="">All Statuses</option>
          <option value="New">New</option>
          <option value="Contacted">Contacted</option>
          <option value="Document Sent">Document Sent</option>
          <option value="Contract Signed">Contract Signed</option>
          <option value="Complete">Complete</option>
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredLeads.map(lead => (
          <div key={lead.id} className="bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{lead.fields['Client Name']}</h3>
                <p className="text-gray-400">{lead.fields['Property Address']}</p>
                <p className="text-sm text-gray-500">{lead.fields.County}, {lead.fields.State}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">Priority Score</div>
                <div className="text-2xl font-bold text-purple-400">{lead.fields['Priority Score']}/100</div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-900 rounded-lg">
              <div>
                <div className="text-xs text-gray-400 uppercase">Surplus Amount</div>
                <div className="text-lg font-bold text-green-400">${lead.fields['Surplus Amount'].toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Your Fee (30%)</div>
                <div className="text-lg font-bold text-purple-400">${lead.fields['Your Fee (30%)'].toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Status</div>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  lead.fields.Status === 'New' ? 'bg-blue-500/20 text-blue-300' :
                  lead.fields.Status === 'Contacted' ? 'bg-yellow-500/20 text-yellow-300' :
                  lead.fields.Status === 'Contract Signed' ? 'bg-green-500/20 text-green-300' :
                  'bg-gray-700 text-gray-200'
                }`}>
                  {lead.fields.Status}
                </span>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase">Lead Stage</div>
                <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/20 text-indigo-300">
                  {lead.fields['Lead Stage']}
                </span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleGenerateForRocketLawyer(lead.id, 'Initial Notice')}
                  className="px-4 py-2 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium flex items-center gap-2"
                >
                  🚀 Initial Notice → RL
                </button>
                <button
                  onClick={() => handleGenerateForRocketLawyer(lead.id, 'Engagement Agreement')}
                  className="px-4 py-2 bg-green-500/100 text-white rounded-lg hover:bg-green-600 text-sm font-medium flex items-center gap-2"
                >
                  🚀 Contract → RL + eSign
                </button>
                <button
                  onClick={() => handleGenerateForRocketLawyer(lead.id, 'Document Checklist')}
                  className="px-4 py-2 bg-purple-500/100 text-white rounded-lg hover:bg-purple-600 text-sm font-medium flex items-center gap-2"
                >
                  🚀 Checklist → RL
                </button>
                <button
                  onClick={() => handleGenerateForRocketLawyer(lead.id, 'Limited Power of Attorney')}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm font-medium flex items-center gap-2"
                >
                  🚀 POA → RL
                </button>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleMarkSentForSignature(lead.id)}
                  className="px-3 py-1.5 bg-indigo-500/20 text-indigo-300 rounded-lg hover:bg-indigo-500/30 text-sm font-medium"
                >
                  ✅ Mark as Sent for Signature
                </button>
                <select
                  onChange={(e) => {
                    if (e.target.value) {
                      handleUpdateLeadStatus(lead.id, e.target.value);
                      e.target.value = '';
                    }
                  }}
                  className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-sm font-medium hover:bg-gray-600 text-white"
                >
                  <option value="">Change Status</option>
                  <option value="Contacted">Mark as Contacted</option>
                  <option value="Document Sent">Document Sent</option>
                  <option value="Contract Signed">Contract Signed</option>
                  <option value="Documents Submitted">Docs Submitted to County</option>
                  <option value="Awaiting County Response">Awaiting County</option>
                  <option value="Funds Released">Funds Released</option>
                  <option value="Client Paid">Client Paid</option>
                  <option value="Complete">Complete</option>
                </select>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Tasks Tab
  const renderTasks = () => (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold text-white mb-2">📋 Task Queue</h3>
        <p className="text-gray-400">Automated follow-up tasks for your leads</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {tasks.map(task => (
          <div key={task.id} className="bg-gray-800 rounded-lg shadow p-6 border-l-4 border-orange-500">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h4 className="text-lg font-semibold text-white">{task.fields['Task Title']}</h4>
                <p className="text-gray-400 text-sm mt-1">{task.fields['Task Description']}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                task.fields.Priority === 'Critical' ? 'bg-red-500/20 text-red-300' :
                task.fields.Priority === 'High' ? 'bg-orange-500/20 text-orange-300' :
                task.fields.Priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-300' :
                'bg-gray-700 text-gray-200'
              }`}>
                {task.fields.Priority}
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
              <span>📅 Due: {task.fields['Due Date']}</span>
              <span>👤 {task.fields['Assigned To'] || 'Unassigned'}</span>
              <span>🏷️ {task.fields['Task Type']}</span>
            </div>

            <button
              onClick={() => handleCompleteTask(task.id)}
              className="px-4 py-2 bg-green-500/100 text-white rounded-lg hover:bg-green-600 text-sm font-medium"
            >
              ✅ Mark Complete
            </button>
          </div>
        ))}
      </div>

      {tasks.length === 0 && (
        <div className="bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-xl font-semibold text-white mb-2">All caught up!</h3>
          <p className="text-gray-400">No pending tasks at the moment.</p>
        </div>
      )}
    </div>
  );

  // Documents Tab
  const renderDocuments = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4">
        {documents.map(doc => (
          <div key={doc.id} className="bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="text-lg font-semibold text-white">{doc.fields['Document Name']}</h4>
                <div className="flex items-center gap-3 mt-2 text-sm text-gray-400">
                  <span>📄 {doc.fields['Document Type']}</span>
                  <span>📅 {new Date(doc.fields['Generated Date']).toLocaleDateString()}</span>
                  {doc.fields['AI Enhanced'] && <span className="text-purple-400">✨ AI Enhanced</span>}
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                doc.fields.Status === 'Generated' ? 'bg-green-500/20 text-green-300' :
                doc.fields.Status === 'Sent via Email' ? 'bg-blue-500/20 text-blue-300' :
                'bg-gray-700 text-gray-200'
              }`}>
                {doc.fields.Status}
              </span>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setDocumentPreview(doc.fields['Generated Content'])}
                className="px-4 py-2 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium"
              >
                👁️ Preview
              </button>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(doc.fields['Generated Content']);
                  alert('Document copied to clipboard!');
                }}
                className="px-4 py-2 bg-purple-500/100 text-white rounded-lg hover:bg-purple-600 text-sm font-medium"
              >
                📋 Copy
              </button>
            </div>
          </div>
        ))}
      </div>

      {documents.length === 0 && (
        <div className="bg-gray-800 rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-xl font-semibold text-white mb-2">No documents yet</h3>
          <p className="text-gray-400">Generate documents from the Leads tab.</p>
        </div>
      )}
    </div>
  );

  // Mining Tab
  const renderMining = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border border-green-200">
        <h3 className="text-lg font-semibold text-white mb-2">🔍 Lead Mining & Import</h3>
        <p className="text-gray-400">Import leads from CSV/PDF files or mine directly from county websites</p>
      </div>

      {miningInProgress && (
        <div className="bg-blue-500/10 border-l-4 border-blue-500 p-4">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div>
              <p className="font-semibold text-blue-300">Mining in progress...</p>
              <p className="text-sm text-blue-400">This may take 30-60 seconds</p>
            </div>
          </div>
        </div>
      )}

      {/* Method 1: Quick CSV Import */}
      <div className="bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">📊</span>
          <h4 className="text-lg font-semibold">Method 1: Quick CSV Import</h4>
          <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full font-medium">Easiest</span>
        </div>
        <p className="text-gray-400 mb-4">
          Upload any CSV with lead data. Works with any column names.
        </p>
        <input
          type="file"
          accept=".csv"
          onChange={handleImportCSV}
          disabled={miningInProgress}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-500/10 file:text-blue-400 hover:file:bg-blue-500/30 disabled:opacity-50"
        />
        <p className="text-xs text-gray-500 mt-2">
          Supports columns: client_name, property, city, county, state, surplus_amount, case_number, phone, email
        </p>
      </div>

      {/* Method 2: County-Specific Upload */}
      <div className="bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">📄</span>
          <h4 className="text-lg font-semibold">Method 2: County PDF/CSV Upload</h4>
          <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full font-medium">Most Accurate</span>
        </div>
        <p className="text-gray-400 mb-4">
          Upload surplus lists directly from county websites (PDF or CSV format)
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">County</label>
            <input
              type="text"
              value={miningCounty}
              onChange={(e) => setMiningCounty(e.target.value)}
              placeholder="e.g., Wayne, Fulton, Harris"
              disabled={miningInProgress}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-white placeholder-gray-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">State</label>
            <select
              value={miningState}
              onChange={(e) => setMiningState(e.target.value)}
              disabled={miningInProgress}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-white"
            >
              <option value="">Select State</option>
              <option value="MI">Michigan</option>
              <option value="GA">Georgia</option>
              <option value="MD">Maryland</option>
              <option value="TX">Texas</option>
              <option value="CA">California</option>
              <option value="IL">Illinois</option>
              <option value="FL">Florida</option>
              <option value="NY">New York</option>
              <option value="PA">Pennsylvania</option>
              <option value="OH">Ohio</option>
              <option value="NC">North Carolina</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Upload PDF</label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleUploadPDF}
              disabled={miningInProgress || !miningCounty || !miningState}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-500/10 file:text-purple-400 hover:file:bg-purple-100 disabled:opacity-50"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Upload CSV</label>
            <input
              type="file"
              accept=".csv"
              onChange={handleUploadCountyCSV}
              disabled={miningInProgress || !miningCounty || !miningState}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-500/10 file:text-green-400 hover:file:bg-green-100 disabled:opacity-50"
            />
          </div>
        </div>
        
        {(!miningCounty || !miningState) && (
          <p className="text-sm text-orange-400 mt-3">⚠️ Select county and state before uploading</p>
        )}
      </div>

      {/* Method 3: Automated Web Scraping */}
      <div className="bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🌐</span>
          <h4 className="text-lg font-semibold">Method 3: Automated County Website Mining</h4>
          <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full font-medium">Automated</span>
        </div>
        <p className="text-gray-400 mb-4">
          Automatically scrape surplus leads from county websites (where configured)
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <button
            onClick={() => handleMineCounty('Wayne', 'MI')}
            disabled={miningInProgress}
            className="px-4 py-3 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🔍 Wayne, MI
          </button>
          <button
            onClick={() => handleMineCounty('Fulton', 'GA')}
            disabled={miningInProgress}
            className="px-4 py-3 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🔍 Fulton, GA
          </button>
          <button
            onClick={() => handleMineCounty('Harris', 'TX')}
            disabled={miningInProgress}
            className="px-4 py-3 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🔍 Harris, TX
          </button>
          <button
            disabled
            className="px-4 py-3 bg-gray-700 text-gray-400 rounded-lg text-sm font-medium cursor-not-allowed"
          >
            🔒 Oakland, MI
          </button>
          <button
            disabled
            className="px-4 py-3 bg-gray-700 text-gray-400 rounded-lg text-sm font-medium cursor-not-allowed"
          >
            🔒 DeKalb, GA
          </button>
          <button
            disabled
            className="px-4 py-3 bg-gray-700 text-gray-400 rounded-lg text-sm font-medium cursor-not-allowed"
          >
            🔒 Baltimore, MD
          </button>
        </div>

        <div className="mt-4 bg-blue-500/10 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-300">
            <strong>Note:</strong> Only 3 counties currently have automated scrapers. For other counties, use Method 2 (PDF/CSV upload) instead.
            New scrapers can be added as needed.
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-6 rounded-lg border border-orange-200">
        <h4 className="text-lg font-semibold text-white mb-3">💡 How to Find Surplus Lists</h4>
        <div className="space-y-2 text-sm text-gray-300">
          <p><strong>1. Visit County Website:</strong> Search "[County Name] treasurer surplus funds" or "[County Name] excess proceeds"</p>
          <p><strong>2. Look For:</strong> Tax sale results, foreclosure surplus, unclaimed property, excess proceeds</p>
          <p><strong>3. Download:</strong> Most counties post PDF or Excel files with surplus lists</p>
          <p><strong>4. Upload Here:</strong> Use Method 2 above to parse and import automatically</p>
        </div>
        <div className="mt-3 pt-3 border-t border-orange-200">
          <p className="text-sm font-semibold text-orange-300">Common URLs:</p>
          <ul className="text-xs text-orange-300 mt-1 space-y-1">
            <li>• Wayne County, MI: waynecounty.com/elected/treasurer</li>
            <li>• Fulton County, GA: fultoncountyga.gov → Real Estate Tax Division</li>
            <li>• Harris County, TX: hctax.net → Property Tax</li>
          </ul>
        </div>
      </div>
    </div>
  );

  // Analytics Tab
  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold mb-4">📊 Lead Distribution</h4>
          <div className="space-y-3">
            {Object.entries(analytics?.leads_by_status || {}).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className="text-gray-300">{status}</span>
                <span className="font-bold text-white">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold mb-4">🎯 Key Metrics</h4>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-400">Average Surplus</div>
              <div className="text-2xl font-bold text-green-400">
                ${(analytics?.average_surplus || 0).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Conversion Rate</div>
              <div className="text-2xl font-bold text-blue-400">
                {analytics?.total_leads ? 
                  ((analytics.contracts_signed / analytics.total_leads) * 100).toFixed(1) 
                  : 0}%
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold mb-4">💰 Revenue Potential</h4>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-400">Total Pipeline</div>
              <div className="text-2xl font-bold text-purple-400">
                ${(analytics?.total_surplus || 0).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Expected Fees</div>
              <div className="text-2xl font-bold text-green-400">
                ${(analytics?.total_fees || 0).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">LBPC - Surplus Recovery System</h1>
          <p className="text-purple-200">Lancaster Banques P.C. • Nationwide Surplus Recovery Services</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto">
          <div className="flex space-x-1 overflow-x-auto">
            {[
              { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
              { id: 'leads', label: '👥 Leads', icon: '👥' },
              { id: 'tasks', label: '✅ Tasks', icon: '✅' },
              { id: 'documents', label: '📄 Documents', icon: '📄' },
              { id: 'mining', label: '🔍 Mining', icon: '🔍' },
              { id: 'analytics', label: '📈 Analytics', icon: '📈' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-b-2 border-purple-500 text-purple-400 bg-gray-700/50'
                    : 'text-gray-400 hover:text-gray-300 hover:bg-gray-700/30'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading...</p>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'leads' && renderLeads()}
            {activeTab === 'tasks' && renderTasks()}
            {activeTab === 'documents' && renderDocuments()}
            {activeTab === 'mining' && renderMining()}
            {activeTab === 'analytics' && renderAnalytics()}
          </>
        )}
      </div>

      {/* Document Preview Modal */}
      {documentPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-700 flex items-center justify-between">
              <h3 className="text-xl font-bold">Document Preview</h3>
              <button
                onClick={() => setDocumentPreview(null)}
                className="text-gray-400 hover:text-white text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <pre className="whitespace-pre-wrap font-mono text-sm bg-gray-900 p-4 rounded">
                {documentPreview}
              </pre>
            </div>
            <div className="p-6 border-t border-gray-700 flex gap-3">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(documentPreview);
                  alert('Copied to clipboard!');
                }}
                className="px-4 py-2 bg-purple-500/100 text-white rounded-lg hover:bg-purple-600"
              >
                📋 Copy to Clipboard
              </button>
              <button
                onClick={() => setDocumentPreview(null)}
                className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rocket Lawyer Workflow Instructions Modal */}
      {showRocketLawyerModal && rocketLawyerInstructions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold flex items-center gap-2">
                    🚀 Rocket Lawyer + Adobe Sign Workflow
                  </h3>
                  <p className="text-orange-100 mt-1">Document: {rocketLawyerInstructions.docType}</p>
                </div>
                <button
                  onClick={() => {
                    setShowRocketLawyerModal(false);
                    setRocketLawyerInstructions(null);
                  }}
                  className="text-white hover:text-orange-100 text-3xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-[70vh]">
              {/* Success Message */}
              <div className="bg-green-500/10 border-l-4 border-green-500 p-4 mb-6">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">✅</div>
                  <div>
                    <h4 className="font-bold text-green-300">Document Generated & Copied!</h4>
                    <p className="text-green-400 text-sm">
                      The document has been copied to your clipboard and Rocket Lawyer has been opened in a new tab.
                    </p>
                  </div>
                </div>
              </div>

              {/* Step-by-Step Instructions */}
              <div className="space-y-4 mb-6">
                <h4 className="text-lg font-bold text-white">📋 Next Steps (2 minutes):</h4>
                
                <div className="space-y-3">
                  <div className="flex gap-4 items-start bg-blue-500/10 p-4 rounded-lg">
                    <div className="bg-blue-500/100 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">1</div>
                    <div>
                      <h5 className="font-semibold text-blue-300">Switch to Rocket Lawyer Tab</h5>
                      <p className="text-blue-400 text-sm">Rocket Lawyer dashboard should be open in a new browser tab.</p>
                    </div>
                  </div>

                  <div className="flex gap-4 items-start bg-purple-500/10 p-4 rounded-lg">
                    <div className="bg-purple-500/100 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">2</div>
                    <div>
                      <h5 className="font-semibold text-purple-300">Create New Document or Use Template</h5>
                      <p className="text-purple-400 text-sm">
                        Click "Create Document" → "Blank Document" or use an existing template
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4 items-start bg-green-500/10 p-4 rounded-lg">
                    <div className="bg-green-500/100 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">3</div>
                    <div>
                      <h5 className="font-semibold text-green-300">Paste Document Content</h5>
                      <p className="text-green-400 text-sm">
                        Press <kbd className="px-2 py-1 bg-gray-800 rounded border">Ctrl+V</kbd> (or <kbd className="px-2 py-1 bg-gray-800 rounded border">Cmd+V</kbd> on Mac) to paste
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4 items-start bg-orange-500/10 p-4 rounded-lg">
                    <div className="bg-orange-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">4</div>
                    <div>
                      <h5 className="font-semibold text-orange-300">Add Branding (Optional)</h5>
                      <p className="text-orange-400 text-sm">Add your logo, letterhead, or any formatting</p>
                    </div>
                  </div>

                  {rocketLawyerInstructions.docType === 'Engagement Agreement' && (
                    <div className="flex gap-4 items-start bg-red-500/10 p-4 rounded-lg border-2 border-red-200">
                      <div className="bg-red-500/100 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">5</div>
                      <div>
                        <h5 className="font-semibold text-red-300">📝 Send for E-Signature (Adobe Sign)</h5>
                        <p className="text-red-400 text-sm mb-2">
                          <strong>Click "Send for Signature"</strong> button in Rocket Lawyer
                        </p>
                        <ul className="text-red-400 text-sm list-disc list-inside space-y-1">
                          <li>Enter client's email address</li>
                          <li>Adobe Sign automatically sends e-signature request</li>
                          <li>Client receives email with signing link</li>
                          <li>You'll be notified when they sign</li>
                        </ul>
                      </div>
                    </div>
                  )}

                  {rocketLawyerInstructions.docType !== 'Engagement Agreement' && (
                    <div className="flex gap-4 items-start bg-indigo-500/10 p-4 rounded-lg">
                      <div className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">5</div>
                      <div>
                        <h5 className="font-semibold text-indigo-300">Download or Send</h5>
                        <p className="text-indigo-400 text-sm">
                          Download as PDF or send directly to client via email
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-4 items-start bg-gray-900 p-4 rounded-lg">
                    <div className="bg-gray-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">6</div>
                    <div>
                      <h5 className="font-semibold text-white">Return to LBPC & Update Status</h5>
                      <p className="text-gray-300 text-sm">
                        Come back here and click <strong>"Mark as Sent for Signature"</strong> button
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Links */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-white mb-3">🔗 Quick Links</h4>
                <div className="flex flex-wrap gap-2">
                  <a
                    href="https://www.rocketlawyer.com/dashboard"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-blue-500/100 text-white rounded-lg hover:bg-blue-600 text-sm font-medium"
                  >
                    🚀 Open Rocket Lawyer
                  </a>
                  <a
                    href="https://www.rocketlawyer.com/documents"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-purple-500/100 text-white rounded-lg hover:bg-purple-600 text-sm font-medium"
                  >
                    📄 My Documents
                  </a>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(rocketLawyerInstructions.content);
                      alert('✅ Document re-copied to clipboard!');
                    }}
                    className="px-4 py-2 bg-green-500/100 text-white rounded-lg hover:bg-green-600 text-sm font-medium"
                  >
                    📋 Copy Again
                  </button>
                </div>
              </div>

              {/* Time Estimate */}
              <div className="mt-4 text-center text-sm text-gray-400">
                ⏱️ <strong>Estimated time:</strong> 2-3 minutes
              </div>
            </div>

            <div className="p-6 border-t border-gray-700 bg-gray-900">
              <button
                onClick={() => {
                  setShowRocketLawyerModal(false);
                  setRocketLawyerInstructions(null);
                }}
                className="w-full px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 font-medium"
              >
                Got it! Close Instructions
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
