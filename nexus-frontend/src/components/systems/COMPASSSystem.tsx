import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../api/client';

interface COMPASSSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface Contract {
  id: string;
  contract_number: string;
  title: string;
  agency: string;
  value: number;
  type: string;
  status: string;
  start_date: string;
  end_date: string;
  pop: string;
  co_name: string;
  co_email: string;
  cor_name: string;
  naics: string;
  set_aside: string;
  health_score: number;
  compliance_status: string;
  invoiced_amount: number;
  paid_amount: number;
  deliverables_total: number;
  deliverables_complete: number;
  next_report_due: string;
  cpars_rating: string;
}

interface Deliverable {
  id: string;
  title: string;
  status: string;
  due_date: string;
  completed_date: string;
  type: string;
}

interface Communication {
  id: string;
  date: string;
  type: string;
  direction: string;
  subject: string;
  summary: string;
  contact: string;
  follow_up: boolean;
  follow_up_date: string;
}

interface Modification {
  id: string;
  mod_number: string;
  type: string;
  description: string;
  value_change: number;
  status: string;
  date: string;
}

interface HealthReport {
  health_score: number;
  status: string;
  components: Record<string, { score: number; weight: number; detail: string }>;
  cpars_prediction: string;
  overdue_deliverables: number;
}

interface Stats {
  active_contracts: number;
  total_contracts: number;
  total_value: number;
  invoiced: number;
  paid: number;
  outstanding: number;
  deliverables_total: number;
  deliverables_complete: number;
  deliverables_pending: number;
  health_avg: number;
}

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'contracts', label: 'Contracts', icon: '📋' },
  { id: 'deliverables', label: 'Deliverables', icon: '📦' },
  { id: 'communications', label: 'CO Comms', icon: '💬' },
  { id: 'modifications', label: 'Modifications', icon: '📝' },
  { id: 'performance', label: 'Performance', icon: '🏥' },
];

const STATUS_COLORS: Record<string, string> = {
  Active: 'bg-green-500/20 text-green-400 border-green-500/30',
  Completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Close-Out': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Suspended: 'bg-red-500/20 text-red-400 border-red-500/30',
  Pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

const HEALTH_COLORS: Record<string, string> = {
  Green: 'text-green-400',
  Yellow: 'text-amber-400',
  Red: 'text-red-400',
};

const COMPASSSystem: React.FC<COMPASSSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [deliverables, setDeliverables] = useState<Deliverable[]>([]);
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [modifications, setModifications] = useState<Modification[]>([]);
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [showContractForm, setShowContractForm] = useState(false);
  const [showDeliverableForm, setShowDeliverableForm] = useState(false);
  const [showCommForm, setShowCommForm] = useState(false);
  const [showModForm, setShowModForm] = useState(false);

  const [contractForm, setContractForm] = useState({
    contract_number: '', title: '', agency: '', value: 0, type: 'Firm Fixed Price',
    start_date: '', end_date: '', pop: '', co_name: '', co_email: '', cor_name: '',
    naics: '', set_aside: '',
  });

  const [deliverableForm, setDeliverableForm] = useState({
    title: '', type: 'Report', due_date: '', description: '', clin: '',
  });

  const [commForm, setCommForm] = useState({
    type: 'Email', direction: 'Outbound', subject: '', summary: '', contact: '',
    follow_up: false, follow_up_date: '',
  });

  const [modForm, setModForm] = useState({
    mod_number: '', type: 'Administrative', description: '', value_change: 0, status: 'Pending',
  });

  const notify = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const loadStats = useCallback(async () => {
    try {
      const res = await api.get('/compass/stats');
      setStats(res); // API returns data directly, not wrapped in .data
    } catch { /* no stats yet */ }
  }, []);

  const loadContracts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/compass/contracts');
      setContracts(res.contracts || []); // API returns { contracts: [...] }
    } catch { setContracts([]); }
    setLoading(false);
  }, []);

  const loadContractDetail = useCallback(async (id: string) => {
    try {
      const res = await api.get(`/compass/contracts/${id}`);
      setDeliverables(res.deliverables || []);
      setCommunications(res.communications || []);
      setModifications(res.modifications || []);
    } catch { /* empty */ }
  }, []);

  const loadHealth = useCallback(async (id: string) => {
    try {
      const res = await api.get(`/compass/contracts/${id}/health`);
      setHealthReport(res); // API returns data directly
    } catch { setHealthReport(null); }
  }, []);

  useEffect(() => {
    loadStats();
    loadContracts();
  }, [loadStats, loadContracts]);

  useEffect(() => {
    if (selectedContract) {
      loadContractDetail(selectedContract.id);
      loadHealth(selectedContract.id);
    }
  }, [selectedContract, loadContractDetail, loadHealth]);

  const createContract = async () => {
    try {
      await api.post('/compass/contracts', contractForm);
      notify('Contract registered in COMPASS');
      setShowContractForm(false);
      setContractForm({ contract_number: '', title: '', agency: '', value: 0, type: 'Firm Fixed Price', start_date: '', end_date: '', pop: '', co_name: '', co_email: '', cor_name: '', naics: '', set_aside: '' });
      loadContracts();
      loadStats();
    } catch { notify('Failed to create contract', 'error'); }
  };

  const createDeliverable = async () => {
    if (!selectedContract) return;
    try {
      await api.post('/compass/deliverables', { ...deliverableForm, contract_id: selectedContract.id });
      notify('Deliverable added');
      setShowDeliverableForm(false);
      setDeliverableForm({ title: '', type: 'Report', due_date: '', description: '', clin: '' });
      loadContractDetail(selectedContract.id);
      loadHealth(selectedContract.id);
    } catch { notify('Failed to add deliverable', 'error'); }
  };

  const completeDeliverable = async (id: string) => {
    try {
      await api.put(`/compass/deliverables/${id}`, { status: 'Completed' });
      notify('Deliverable marked complete');
      if (selectedContract) {
        loadContractDetail(selectedContract.id);
        loadHealth(selectedContract.id);
      }
    } catch { notify('Failed to update', 'error'); }
  };

  const logComm = async () => {
    if (!selectedContract) return;
    try {
      await api.post('/compass/communications', { ...commForm, contract_id: selectedContract.id });
      notify('Communication logged');
      setShowCommForm(false);
      setCommForm({ type: 'Email', direction: 'Outbound', subject: '', summary: '', contact: '', follow_up: false, follow_up_date: '' });
      loadContractDetail(selectedContract.id);
    } catch { notify('Failed to log communication', 'error'); }
  };

  const createMod = async () => {
    if (!selectedContract) return;
    try {
      await api.post('/compass/modifications', { ...modForm, contract_id: selectedContract.id });
      notify('Modification logged');
      setShowModForm(false);
      setModForm({ mod_number: '', type: 'Administrative', description: '', value_change: 0, status: 'Pending' });
      loadContractDetail(selectedContract.id);
    } catch { notify('Failed to create modification', 'error'); }
  };

  const generateReport = async () => {
    if (!selectedContract) return;
    try {
      const res = await api.post(`/compass/contracts/${selectedContract.id}/performance-report`);
      notify('Performance report generated');
      console.log('Report:', res.report); // API returns data directly
    } catch { notify('Failed to generate report', 'error'); }
  };

  const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n);

  // ─── DASHBOARD TAB ─────────────────────────────────────────────────────
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Contracts', value: stats?.active_contracts || 0, color: 'text-green-400' },
          { label: 'Total Value', value: fmt(stats?.total_value || 0), color: 'text-blue-400' },
          { label: 'Invoiced', value: fmt(stats?.invoiced || 0), color: 'text-purple-400' },
          { label: 'Outstanding', value: fmt(stats?.outstanding || 0), color: stats?.outstanding ? 'text-amber-400' : 'text-gray-400' },
        ].map((s, i) => (
          <div key={i} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
            <div className="text-sm text-gray-400">{s.label}</div>
            <div className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Deliverables Pending', value: stats?.deliverables_pending || 0, color: 'text-amber-400' },
          { label: 'Deliverables Complete', value: stats?.deliverables_complete || 0, color: 'text-green-400' },
          { label: 'Avg Health Score', value: `${stats?.health_avg || 0}%`, color: (stats?.health_avg || 0) >= 85 ? 'text-green-400' : (stats?.health_avg || 0) >= 65 ? 'text-amber-400' : 'text-red-400' },
          { label: 'Paid', value: fmt(stats?.paid || 0), color: 'text-emerald-400' },
        ].map((s, i) => (
          <div key={i} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
            <div className="text-sm text-gray-400">{s.label}</div>
            <div className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Quick Contract List */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Active Contracts</h3>
          <button onClick={() => setShowContractForm(true)} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
            + Register Contract
          </button>
        </div>
        {contracts.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-3">🧭</div>
            <p className="text-lg">No contracts registered yet</p>
            <p className="text-sm mt-1">When you win a contract through GPSS, COMPASS auto-registers it for post-award management.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {contracts.slice(0, 8).map(c => (
              <div key={c.id}
                onClick={() => { setSelectedContract(c); setActiveTab('contracts'); }}
                className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-blue-500/50 cursor-pointer transition">
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${c.compliance_status === 'Green' ? 'bg-green-500' : c.compliance_status === 'Yellow' ? 'bg-amber-500' : 'bg-red-500'}`} />
                  <div>
                    <div className="font-medium">{c.title}</div>
                    <div className="text-sm text-gray-400">{c.agency} — {c.contract_number}</div>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div>
                    <span className="text-gray-500">Value</span>
                    <div className="font-medium text-blue-400">{fmt(c.value)}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Deliverables</span>
                    <div className="font-medium">{c.deliverables_complete}/{c.deliverables_total}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Health</span>
                    <div className={`font-bold ${HEALTH_COLORS[c.compliance_status] || 'text-gray-400'}`}>{c.health_score}%</div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs border ${STATUS_COLORS[c.status] || STATUS_COLORS.Pending}`}>
                    {c.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  // ─── CONTRACTS TAB ─────────────────────────────────────────────────────
  const renderContracts = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Contract Registry</h3>
        <button onClick={() => setShowContractForm(true)} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
          + Register Contract
        </button>
      </div>

      {selectedContract ? (
        <div className="space-y-6">
          <button onClick={() => setSelectedContract(null)} className="text-sm text-blue-400 hover:text-blue-300">&larr; Back to all contracts</button>
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-bold">{selectedContract.title}</h2>
                <div className="text-gray-400 mt-1">{selectedContract.agency} — {selectedContract.contract_number}</div>
                <div className="flex items-center gap-4 mt-3 text-sm">
                  <span className={`px-3 py-1 rounded-full text-xs border ${STATUS_COLORS[selectedContract.status] || STATUS_COLORS.Pending}`}>
                    {selectedContract.status}
                  </span>
                  <span className="text-gray-500">Type: {selectedContract.type}</span>
                  <span className="text-gray-500">NAICS: {selectedContract.naics}</span>
                  {selectedContract.set_aside && <span className="text-green-400">Set-Aside: {selectedContract.set_aside}</span>}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-400">{fmt(selectedContract.value)}</div>
                <div className={`text-lg font-bold ${HEALTH_COLORS[selectedContract.compliance_status] || ''}`}>
                  Health: {selectedContract.health_score}%
                </div>
              </div>
            </div>

            {/* Key Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              {[
                { label: 'CO', value: selectedContract.co_name || 'Not set' },
                { label: 'CO Email', value: selectedContract.co_email || 'Not set' },
                { label: 'COR', value: selectedContract.cor_name || 'Not set' },
                { label: 'POP', value: selectedContract.pop || `${selectedContract.start_date} to ${selectedContract.end_date}` },
                { label: 'Invoiced', value: fmt(selectedContract.invoiced_amount || 0) },
                { label: 'Paid', value: fmt(selectedContract.paid_amount || 0) },
                { label: 'Deliverables', value: `${selectedContract.deliverables_complete}/${selectedContract.deliverables_total}` },
                { label: 'Next Report', value: selectedContract.next_report_due || 'Not scheduled' },
              ].map((item, i) => (
                <div key={i} className="bg-gray-700/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500">{item.label}</div>
                  <div className="font-medium text-sm mt-1 truncate">{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {contracts.map(c => (
            <div key={c.id}
              onClick={() => setSelectedContract(c)}
              className="flex items-center justify-between p-4 bg-gray-800 rounded-xl border border-gray-700 hover:border-blue-500/50 cursor-pointer transition">
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${c.compliance_status === 'Green' ? 'bg-green-500' : c.compliance_status === 'Yellow' ? 'bg-amber-500' : 'bg-red-500'}`} />
                <div>
                  <div className="font-medium">{c.title}</div>
                  <div className="text-sm text-gray-400">{c.agency} — {c.contract_number}</div>
                </div>
              </div>
              <div className="flex items-center gap-6 text-sm">
                <div className="text-blue-400 font-medium">{fmt(c.value)}</div>
                <div>{c.deliverables_complete}/{c.deliverables_total} del.</div>
                <div className={`font-bold ${HEALTH_COLORS[c.compliance_status] || ''}`}>{c.health_score}%</div>
                <span className={`px-3 py-1 rounded-full text-xs border ${STATUS_COLORS[c.status] || STATUS_COLORS.Pending}`}>
                  {c.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // ─── DELIVERABLES TAB ──────────────────────────────────────────────────
  const renderDeliverables = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Deliverables {selectedContract ? `— ${selectedContract.title}` : ''}
        </h3>
        <div className="flex gap-3">
          {!selectedContract && contracts.length > 0 && (
            <select onChange={e => { const c = contracts.find(x => x.id === e.target.value); if (c) setSelectedContract(c); }}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm">
              <option value="">Select Contract</option>
              {contracts.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
            </select>
          )}
          {selectedContract && (
            <button onClick={() => setShowDeliverableForm(true)} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
              + Add Deliverable
            </button>
          )}
        </div>
      </div>

      {!selectedContract ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📦</div>
          <p>Select a contract to view deliverables</p>
        </div>
      ) : deliverables.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📦</div>
          <p>No deliverables yet for this contract</p>
          <p className="text-sm mt-1">Add deliverables to track what you owe the CO.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {deliverables.map(d => {
            const overdue = d.status !== 'Completed' && d.due_date && d.due_date < new Date().toISOString().split('T')[0];
            return (
              <div key={d.id} className={`flex items-center justify-between p-4 bg-gray-800 rounded-xl border ${overdue ? 'border-red-500/50' : 'border-gray-700'}`}>
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${d.status === 'Completed' ? 'bg-green-500/20 text-green-400' : overdue ? 'bg-red-500/20 text-red-400' : 'bg-gray-700 text-gray-400'}`}>
                    {d.status === 'Completed' ? '✓' : overdue ? '!' : '○'}
                  </div>
                  <div>
                    <div className={`font-medium ${d.status === 'Completed' ? 'line-through text-gray-500' : ''}`}>{d.title}</div>
                    <div className="text-sm text-gray-400">
                      {d.type} — Due: {d.due_date || 'No date'}
                      {d.completed_date && ` — Completed: ${d.completed_date}`}
                      {overdue && <span className="text-red-400 ml-2 font-medium">OVERDUE</span>}
                    </div>
                  </div>
                </div>
                {d.status !== 'Completed' && (
                  <button onClick={() => completeDeliverable(d.id)}
                    className="bg-green-500/20 hover:bg-green-500/30 text-green-400 px-4 py-2 rounded-lg text-sm transition">
                    Mark Complete
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  // ─── COMMUNICATIONS TAB ────────────────────────────────────────────────
  const renderCommunications = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          CO/COR Communications {selectedContract ? `— ${selectedContract.title}` : ''}
        </h3>
        <div className="flex gap-3">
          {!selectedContract && contracts.length > 0 && (
            <select onChange={e => { const c = contracts.find(x => x.id === e.target.value); if (c) setSelectedContract(c); }}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm">
              <option value="">Select Contract</option>
              {contracts.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
            </select>
          )}
          {selectedContract && (
            <button onClick={() => setShowCommForm(true)} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
              + Log Communication
            </button>
          )}
        </div>
      </div>

      {!selectedContract ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">💬</div>
          <p>Select a contract to view CO communications</p>
        </div>
      ) : communications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">💬</div>
          <p>No communications logged yet</p>
          <p className="text-sm mt-1">Log every CO/COR interaction — email, phone, meeting. Documentation protects DDI.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {communications.map(c => (
            <div key={c.id} className="p-4 bg-gray-800 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${c.direction === 'Outbound' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                    {c.direction === 'Outbound' ? '→ Sent' : '← Received'}
                  </span>
                  <span className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">{c.type}</span>
                  <span className="font-medium">{c.subject}</span>
                </div>
                <div className="text-sm text-gray-400">{c.date}</div>
              </div>
              <div className="text-sm text-gray-400 mt-2">{c.summary}</div>
              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                <span>Contact: {c.contact}</span>
                {c.follow_up && <span className="text-amber-400 font-medium">Follow-up: {c.follow_up_date || 'Needed'}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // ─── MODIFICATIONS TAB ─────────────────────────────────────────────────
  const renderModifications = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Contract Modifications {selectedContract ? `— ${selectedContract.title}` : ''}
        </h3>
        <div className="flex gap-3">
          {!selectedContract && contracts.length > 0 && (
            <select onChange={e => { const c = contracts.find(x => x.id === e.target.value); if (c) setSelectedContract(c); }}
              className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm">
              <option value="">Select Contract</option>
              {contracts.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
            </select>
          )}
          {selectedContract && (
            <button onClick={() => setShowModForm(true)} className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-sm font-medium transition">
              + Log Modification
            </button>
          )}
        </div>
      </div>

      {!selectedContract ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📝</div>
          <p>Select a contract to view modifications</p>
        </div>
      ) : modifications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📝</div>
          <p>No modifications logged</p>
          <p className="text-sm mt-1">Track every contract mod — scope changes, value adjustments, option years, admin changes.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {modifications.map(m => (
            <div key={m.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-xl border border-gray-700">
              <div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-blue-400">{m.mod_number}</span>
                  <span className="px-2 py-1 rounded text-xs bg-gray-700">{m.type}</span>
                  <span className={`px-2 py-1 rounded text-xs ${m.status === 'Executed' ? 'bg-green-500/20 text-green-400' : 'bg-amber-500/20 text-amber-400'}`}>
                    {m.status}
                  </span>
                </div>
                <div className="text-sm text-gray-400 mt-1">{m.description}</div>
              </div>
              <div className="text-right">
                <div className={`font-bold ${m.value_change > 0 ? 'text-green-400' : m.value_change < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                  {m.value_change > 0 ? '+' : ''}{fmt(m.value_change)}
                </div>
                <div className="text-xs text-gray-500">{m.date}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // ─── PERFORMANCE TAB ───────────────────────────────────────────────────
  const renderPerformance = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Contract Health & Performance {selectedContract ? `— ${selectedContract.title}` : ''}
        </h3>
        {selectedContract && (
          <button onClick={generateReport} className="bg-purple-500 hover:bg-purple-600 px-4 py-2 rounded-lg text-sm font-medium transition">
            Generate Monthly Report
          </button>
        )}
      </div>

      {!selectedContract ? (
        <div className="space-y-6">
          {/* Portfolio Health Overview */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h4 className="font-semibold mb-4">Portfolio Health Overview</h4>
            {contracts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No contracts to analyze</div>
            ) : (
              <div className="space-y-3">
                {contracts.filter(c => c.status === 'Active').map(c => (
                  <div key={c.id}
                    onClick={() => setSelectedContract(c)}
                    className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg cursor-pointer hover:bg-gray-700 transition">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${c.health_score >= 85 ? 'bg-green-500/20 text-green-400' : c.health_score >= 65 ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'}`}>
                        {c.health_score}
                      </div>
                      <div>
                        <div className="font-medium">{c.title}</div>
                        <div className="text-sm text-gray-400">{c.agency}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <div><span className="text-gray-500">Del.</span> {c.deliverables_complete}/{c.deliverables_total}</div>
                      <div><span className="text-gray-500">Invoiced</span> {fmt(c.invoiced_amount || 0)}</div>
                      <div><span className="text-gray-500">Paid</span> {fmt(c.paid_amount || 0)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : healthReport ? (
        <div className="space-y-6">
          <button onClick={() => setSelectedContract(null)} className="text-sm text-blue-400 hover:text-blue-300">&larr; Portfolio view</button>

          {/* Health Score */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h4 className="text-lg font-semibold">Contract Health Score</h4>
                <p className="text-sm text-gray-400 mt-1">Composite score based on delivery, payment, burn rate, and timeliness</p>
              </div>
              <div className={`text-5xl font-bold ${healthReport.status === 'Green' ? 'text-green-400' : healthReport.status === 'Yellow' ? 'text-amber-400' : 'text-red-400'}`}>
                {healthReport.health_score}%
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(healthReport.components).map(([key, comp]) => (
                <div key={key} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 capitalize">{key.replace('_', ' ')}</div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className={`text-2xl font-bold ${comp.score >= 85 ? 'text-green-400' : comp.score >= 65 ? 'text-amber-400' : 'text-red-400'}`}>
                      {comp.score}
                    </span>
                    <span className="text-xs text-gray-500">/ 100 ({comp.weight}% weight)</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{comp.detail}</div>
                </div>
              ))}
            </div>
          </div>

          {/* CPARS Prediction */}
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h4 className="font-semibold mb-2">CPARS Rating Prediction</h4>
            <p className={`text-lg font-medium ${healthReport.status === 'Green' ? 'text-green-400' : healthReport.status === 'Yellow' ? 'text-amber-400' : 'text-red-400'}`}>
              {healthReport.cpars_prediction}
            </p>
            {healthReport.overdue_deliverables > 0 && (
              <p className="text-red-400 text-sm mt-2">
                {healthReport.overdue_deliverables} overdue deliverable{healthReport.overdue_deliverables > 1 ? 's' : ''} — fix this before it hits your CPARS.
              </p>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">Loading health data...</div>
      )}
    </div>
  );

  // ─── MODALS ────────────────────────────────────────────────────────────
  const renderContractModal = () => showContractForm && (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowContractForm(false)}>
      <div className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto border border-gray-700" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">Register Contract</h3>
        <div className="grid grid-cols-2 gap-4">
          {[
            { key: 'contract_number', label: 'Contract Number', placeholder: 'e.g. GS-07F-1234' },
            { key: 'title', label: 'Title', placeholder: 'Contract title' },
            { key: 'agency', label: 'Agency', placeholder: 'e.g. USACE, VA, GSA' },
            { key: 'co_name', label: 'CO Name', placeholder: 'Contracting Officer' },
            { key: 'co_email', label: 'CO Email', placeholder: 'co@agency.gov' },
            { key: 'cor_name', label: 'COR Name', placeholder: 'Contracting Officer Rep' },
            { key: 'naics', label: 'NAICS', placeholder: 'e.g. 561612' },
            { key: 'set_aside', label: 'Set-Aside', placeholder: 'e.g. EDWOSB, WOSB' },
            { key: 'start_date', label: 'Start Date', type: 'date' },
            { key: 'end_date', label: 'End Date', type: 'date' },
            { key: 'pop', label: 'Period of Performance', placeholder: 'e.g. 12 months + 4 option years' },
          ].map(f => (
            <div key={f.key}>
              <label className="text-xs text-gray-400">{f.label}</label>
              <input
                type={f.type || 'text'}
                value={(contractForm as any)[f.key] || ''}
                onChange={e => setContractForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                placeholder={f.placeholder}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1"
              />
            </div>
          ))}
          <div>
            <label className="text-xs text-gray-400">Value ($)</label>
            <input type="number" value={contractForm.value}
              onChange={e => setContractForm(prev => ({ ...prev, value: Number(e.target.value) }))}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Contract Type</label>
            <select value={contractForm.type}
              onChange={e => setContractForm(prev => ({ ...prev, type: e.target.value }))}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
              {['Firm Fixed Price', 'Time & Materials', 'Cost Reimbursable', 'IDIQ', 'BPA', 'GSA Schedule'].map(t => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setShowContractForm(false)} className="px-4 py-2 bg-gray-700 rounded-lg text-sm">Cancel</button>
          <button onClick={createContract} className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium">Register Contract</button>
        </div>
      </div>
    </div>
  );

  const renderDeliverableModal = () => showDeliverableForm && (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowDeliverableForm(false)}>
      <div className="bg-gray-800 rounded-xl p-6 max-w-lg w-full mx-4 border border-gray-700" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">Add Deliverable</h3>
        <div className="space-y-4">
          <div>
            <label className="text-xs text-gray-400">Title</label>
            <input value={deliverableForm.title} onChange={e => setDeliverableForm(p => ({ ...p, title: e.target.value }))}
              placeholder="e.g. Monthly Status Report - March" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-400">Type</label>
              <select value={deliverableForm.type} onChange={e => setDeliverableForm(p => ({ ...p, type: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
                {['Report', 'Product', 'Service', 'Milestone', 'Training', 'Documentation', 'Inspection'].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400">Due Date</label>
              <input type="date" value={deliverableForm.due_date} onChange={e => setDeliverableForm(p => ({ ...p, due_date: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-400">CLIN Reference</label>
            <input value={deliverableForm.clin} onChange={e => setDeliverableForm(p => ({ ...p, clin: e.target.value }))}
              placeholder="e.g. CLIN 0001" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Description</label>
            <textarea value={deliverableForm.description} onChange={e => setDeliverableForm(p => ({ ...p, description: e.target.value }))}
              rows={3} placeholder="What needs to be delivered..." className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setShowDeliverableForm(false)} className="px-4 py-2 bg-gray-700 rounded-lg text-sm">Cancel</button>
          <button onClick={createDeliverable} className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium">Add Deliverable</button>
        </div>
      </div>
    </div>
  );

  const renderCommModal = () => showCommForm && (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowCommForm(false)}>
      <div className="bg-gray-800 rounded-xl p-6 max-w-lg w-full mx-4 border border-gray-700" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">Log Communication</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-400">Type</label>
              <select value={commForm.type} onChange={e => setCommForm(p => ({ ...p, type: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
                {['Email', 'Phone', 'Meeting', 'Letter', 'WAWF', 'Other'].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400">Direction</label>
              <select value={commForm.direction} onChange={e => setCommForm(p => ({ ...p, direction: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
                <option>Outbound</option>
                <option>Inbound</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-400">Contact</label>
            <input value={commForm.contact} onChange={e => setCommForm(p => ({ ...p, contact: e.target.value }))}
              placeholder="CO/COR name" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Subject</label>
            <input value={commForm.subject} onChange={e => setCommForm(p => ({ ...p, subject: e.target.value }))}
              placeholder="Subject line or topic" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Summary</label>
            <textarea value={commForm.summary} onChange={e => setCommForm(p => ({ ...p, summary: e.target.value }))}
              rows={3} placeholder="Key points discussed..." className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={commForm.follow_up} onChange={e => setCommForm(p => ({ ...p, follow_up: e.target.checked }))} />
              Follow-up required
            </label>
            {commForm.follow_up && (
              <input type="date" value={commForm.follow_up_date} onChange={e => setCommForm(p => ({ ...p, follow_up_date: e.target.value }))}
                className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm" />
            )}
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setShowCommForm(false)} className="px-4 py-2 bg-gray-700 rounded-lg text-sm">Cancel</button>
          <button onClick={logComm} className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium">Log Communication</button>
        </div>
      </div>
    </div>
  );

  const renderModModal = () => showModForm && (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowModForm(false)}>
      <div className="bg-gray-800 rounded-xl p-6 max-w-lg w-full mx-4 border border-gray-700" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold mb-4">Log Contract Modification</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-400">Mod Number</label>
              <input value={modForm.mod_number} onChange={e => setModForm(p => ({ ...p, mod_number: e.target.value }))}
                placeholder="e.g. P00001" className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label className="text-xs text-gray-400">Type</label>
              <select value={modForm.type} onChange={e => setModForm(p => ({ ...p, type: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
                {['Administrative', 'Scope Change', 'Option Year', 'Value Adjustment', 'Termination', 'Extension'].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-400">Value Change ($)</label>
            <input type="number" value={modForm.value_change} onChange={e => setModForm(p => ({ ...p, value_change: Number(e.target.value) }))}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Description</label>
            <textarea value={modForm.description} onChange={e => setModForm(p => ({ ...p, description: e.target.value }))}
              rows={3} placeholder="What this modification changes..." className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Status</label>
            <select value={modForm.status} onChange={e => setModForm(p => ({ ...p, status: e.target.value }))}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm mt-1">
              {['Pending', 'Under Review', 'Executed', 'Rejected'].map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setShowModForm(false)} className="px-4 py-2 bg-gray-700 rounded-lg text-sm">Cancel</button>
          <button onClick={createMod} className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-sm font-medium">Log Modification</button>
        </div>
      </div>
    </div>
  );

  // ─── MAIN RENDER ───────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Tab Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-2">
        <div className="flex items-center gap-2 overflow-x-auto">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
                activeTab === tab.id ? 'bg-teal-500 text-white' : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              }`}>
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Notification */}
        {notification && (
          <div className={`mb-4 p-3 rounded-lg text-sm font-medium ${
            notification.type === 'success' ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-red-500/20 text-red-400 border border-red-500/30'
          }`}>
            {notification.message}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500" />
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'contracts' && renderContracts()}
            {activeTab === 'deliverables' && renderDeliverables()}
            {activeTab === 'communications' && renderCommunications()}
            {activeTab === 'modifications' && renderModifications()}
            {activeTab === 'performance' && renderPerformance()}
          </>
        )}
      </div>

      {/* Modals */}
      {renderContractModal()}
      {renderDeliverableModal()}
      {renderCommModal()}
      {renderModModal()}
    </div>
  );
};

export default COMPASSSystem;
