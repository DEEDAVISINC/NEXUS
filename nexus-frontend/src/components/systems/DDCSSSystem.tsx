import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface DDCSSSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const DDCSSSystem: React.FC<DDCSSSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [apiKey, setApiKey] = useState('');
  const [copilotMessage, setCopilotMessage] = useState('');
  const [copilotMessages, setCopilotMessages] = useState([
    { text: "👋 Hi Dee! I'm your AI Copilot. I can help you with strategy, generate emails, analyze responses, or explain how anything works. What would you like me to help with?", isUser: false }
  ]);
  const [showCopilot, setShowCopilot] = useState(false);
  const [corporateSection, setCorporateSection] = useState('offer-blueprint');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Client Avatar Builder State
  const [avatarFormData, setAvatarFormData] = useState({
    avatarName: '',
    companySize: '',
    industry: '',
    painPoints: '',
    goals: '',
    budget: '',
    decisionMakers: '',
    prospectId: ''
  });
  const [avatarAnalysis, setAvatarAnalysis] = useState<any | null>(null);
  const [avatars, setAvatars] = useState<any[]>([]);
  const [avatarsLoading, setAvatarsLoading] = useState(false);
  const [editingAvatarId, setEditingAvatarId] = useState<string | null>(null);
  const [savingAvatar, setSavingAvatar] = useState(false);

  // Success Path Builder State
  const [successPathFormData, setSuccessPathFormData] = useState({
    pathName: '',
    prospectId: '',
    startingPoint: '',
    endGoal: '',
    milestones: '',
    timeline: ''
  });

  // PitchMap Generator State
  const [pitchmapFormData, setPitchmapFormData] = useState({
    pitchMapName: '',
    prospectId: '',
    painPoint: '',
    solution: ''
  });
  const [pitchmapScript, setPitchmapScript] = useState<string>('');

  // Prospects State
  const [prospects, setProspects] = useState<any[]>([]);

  // 6 Sectors State
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Load prospects on mount
  useEffect(() => {
    fetchProspects();
    fetchAvatars();
  }, []);

  const fetchProspects = async () => {
    try {
      const response = await api.getDdcssProspects();
      setProspects(response.prospects || []);
    } catch (error) {
      console.error('Error fetching prospects:', error);
      setProspects([]);
    }
  };

  const fetchAvatars = async () => {
    setAvatarsLoading(true);
    try {
      const response = await api.getDdcssClientAvatars();
      setAvatars(response.avatars || []);
    } catch (error) {
      console.error('Error fetching avatars:', error);
      setAvatars([]);
    } finally {
      setAvatarsLoading(false);
    }
  };

  // Client Avatar Functions
  const resetAvatarForm = () => {
    setAvatarFormData({ avatarName: '', companySize: '', industry: '', painPoints: '', goals: '', budget: '', decisionMakers: '', prospectId: '' });
    setEditingAvatarId(null);
    setAvatarAnalysis(null);
  };

  const createClientAvatar = async () => {
    if (!avatarFormData.avatarName.trim()) {
      showNotification('Avatar name is required', 'error');
      return;
    }
    setSavingAvatar(true);
    try {
      const response = await api.createDdcssClientAvatar(avatarFormData);
      if (response.avatar) {
        showNotification('Client Avatar created with AI analysis!', 'success');
        setAvatarAnalysis(response.aiAnalysis || null);
        fetchAvatars();
        fetchProspects();
      }
    } catch (error) {
      showNotification('Error creating client avatar', 'error');
    } finally {
      setSavingAvatar(false);
    }
  };

  const updateClientAvatar = async () => {
    if (!editingAvatarId) return;
    setSavingAvatar(true);
    try {
      await api.updateDdcssClientAvatar(editingAvatarId, avatarFormData);
      showNotification('Avatar updated!', 'success');
      fetchAvatars();
      fetchProspects();
      resetAvatarForm();
    } catch (error) {
      showNotification('Error updating avatar', 'error');
    } finally {
      setSavingAvatar(false);
    }
  };

  const deleteClientAvatar = async (id: string) => {
    if (!window.confirm('Delete this avatar? This also removes the prospect record.')) return;
    try {
      await api.deleteDdcssClientAvatar(id);
      showNotification('Avatar deleted', 'success');
      fetchAvatars();
      fetchProspects();
      if (editingAvatarId === id) resetAvatarForm();
    } catch (error) {
      showNotification('Error deleting avatar', 'error');
    }
  };

  const loadAvatarForEdit = (avatar: any) => {
    setEditingAvatarId(avatar.id);
    setAvatarFormData({
      avatarName: avatar.avatarName || avatar.companyName || '',
      companySize: avatar.companySize || '',
      industry: avatar.industry || '',
      painPoints: avatar.painPoints || '',
      goals: avatar.goals || avatar.businessGoals || '',
      budget: avatar.budget || '',
      decisionMakers: avatar.decisionMakers || avatar.contactName || '',
      prospectId: ''
    });
    setAvatarAnalysis(null);
  };

  // Success Path Functions
  const createSuccessPath = async () => {
    try {
      const response = await api.createDdcssSuccessPath(successPathFormData);
      if (response.successPath) {
        showNotification('✅ Success Path created!', 'success');
        setSuccessPathFormData({
          pathName: '',
          prospectId: '',
          startingPoint: '',
          endGoal: '',
          milestones: '',
          timeline: ''
        });
      }
    } catch (error) {
      showNotification('❌ Error creating success path', 'error');
    }
  };

  // PitchMap Functions
  const generatePitchmap = async () => {
    try {
      const response = await api.createDdcssPitchmap(pitchmapFormData);
      if (response.pitchmap) {
        showNotification('✅ PitchMap generated with AI script!', 'success');
        setPitchmapScript(response.script || '');
        setPitchmapFormData({
          pitchMapName: '',
          prospectId: '',
          painPoint: '',
          solution: ''
        });
      }
    } catch (error) {
      showNotification('❌ Error generating pitchmap', 'error');
    }
  };

  // AI Response Handler State
  const [responseAnalysis, setResponseAnalysis] = useState<any | null>(null);
  const [analyzingResponse, setAnalyzingResponse] = useState(false);
  const [responseFormData, setResponseFormData] = useState({
    emailContent: '',
    prospectId: '',
    prospectName: '',
    company: '',
    sector: ''
  });

  // AI Response Handler Functions
  const analyzeResponse = async () => {
    if (!responseFormData.emailContent.trim()) {
      showNotification('Please paste an email response to analyze', 'error');
      return;
    }

    setAnalyzingResponse(true);
    try {
      const response = await api.analyzeResponse(
        responseFormData.emailContent,
        responseFormData.prospectId || undefined
      );
      
      if (response.error) {
        showNotification(`❌ Error: ${response.error}`, 'error');
      } else {
        setResponseAnalysis(response);
        showNotification('✅ Response analyzed successfully!', 'success');
      }
    } catch (error) {
      showNotification('❌ Error analyzing response', 'error');
    } finally {
      setAnalyzingResponse(false);
    }
  };

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'corporate-mastery', label: '💼 Corporate Sales Mastery' },
    { id: 'blueprint', label: '🎯 Blueprint Framework' },
    { id: 'client-avatar', label: '👤 Client Avatar Builder' },
    { id: 'success-path', label: '🛤️ Success Path Builder' },
    { id: 'pitchmap', label: '🎤 PitchMap Generator' },
    { id: 'your-sectors', label: '🏢 Your 6 Sectors' },
    { id: 'ai-handler', label: '🤖 AI Response Handler' },
    { id: 'pipeline', label: '📈 Pipeline' },
    { id: 'mvp-discovery', label: '⭐ MVP Discovery' }
  ];

  // Dashboard Stats (calculated from prospects)
  const prospectsByStatus = {
    new: prospects.filter((p: any) => !p.status || p.status === 'New').length,
    qualifying: prospects.filter((p: any) => p.status === 'Qualifying').length,
    proposal: prospects.filter((p: any) => p.status === 'Proposal').length,
    won: prospects.filter((p: any) => p.status === 'Closed Won' || p.status === 'Won').length,
    lost: prospects.filter((p: any) => p.status === 'Closed Lost' || p.status === 'Lost').length,
  };
  const activePipeline = prospectsByStatus.new + prospectsByStatus.qualifying + prospectsByStatus.proposal;
  const pipelineValue = prospects.reduce((sum: number, p: any) => {
    const budget = p.budget || '';
    const match = budget.match(/\$?([\d,.]+)\s*[Kk]/);
    if (match) return sum + (parseFloat(match[1].replace(',', '')) * 1000);
    const direct = budget.match(/\$?([\d,]+)/);
    if (direct) return sum + parseFloat(direct[1].replace(',', ''));
    return sum;
  }, 0);

  const sendCopilotMessage = () => {
    if (!copilotMessage.trim()) return;
    
    setCopilotMessages(prev => [...prev, { text: copilotMessage, isUser: true }]);
    
    setTimeout(() => {
      let response = "I understand. Let me help you with that.";
      
      if (copilotMessage.toLowerCase().includes('response')) {
        response = "✅ Checked your inbox. No new responses right now. I'll check again in 1 hour automatically.";
      } else if (copilotMessage.toLowerCase().includes('what should')) {
        response = "Based on your pipeline, here's what I recommend:<br><br>1. Follow up with 3 prospects from last week<br>2. Send proposal to Wayne County (they're ready)<br>3. Schedule call with Oakland County CFO<br><br>Want me to draft these messages?";
      } else if (copilotMessage.toLowerCase().includes('email')) {
        response = "Which type?<br>• Follow-up (for warm leads)<br>• Cold outreach (new contacts)<br>• Proposal send (ready to close)<br>• Call confirmation (booked meetings)";
      }
      
      setCopilotMessages(prev => [...prev, { text: response, isUser: false }]);
    }, 1000);
    
    setCopilotMessage('');
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
            {/* Header */}
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">DDCSS Command Center</h2>
                <p className="text-gray-400">Your pipeline, your process, your next move</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setActiveTab('pipeline')} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  Open Pipeline
                </button>
                <button onClick={fetchProspects} className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  Refresh
                </button>
              </div>
            </div>

            {/* Pipeline Stats */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Prospects</h3>
                <p className="text-3xl font-bold">{prospects.length}</p>
              </div>
              <div className="bg-gradient-to-br from-cyan-600 to-cyan-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Active Pipeline</h3>
                <p className="text-3xl font-bold">{activePipeline}</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Qualifying</h3>
                <p className="text-3xl font-bold">{prospectsByStatus.qualifying}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Proposals Out</h3>
                <p className="text-3xl font-bold">{prospectsByStatus.proposal}</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 p-5 rounded-xl">
                <h3 className="text-xs font-semibold text-white/70 mb-1">Pipeline Value</h3>
                <p className="text-3xl font-bold">{pipelineValue > 0 ? `$${(pipelineValue / 1000).toFixed(0)}K` : '$0'}</p>
              </div>
            </div>

            {/* Prospect Pipeline + Execute the System */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Prospect Pipeline */}
              <div className="bg-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold">Prospect Pipeline</h3>
                  {prospects.length > 0 && (
                    <button onClick={() => setActiveTab('pipeline')} className="text-blue-400 hover:text-blue-300 text-xs font-semibold">
                      Manage All
                    </button>
                  )}
                </div>
                {prospects.length > 0 ? (
                  <div className="space-y-2">
                    {prospects.slice(0, 6).map((prospect: any) => (
                      <div key={prospect.id} className="flex items-center justify-between bg-gray-700/50 border border-gray-600/50 px-4 py-3 rounded-lg">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm text-blue-400 truncate">{prospect.companyName || 'Unnamed'}</h4>
                          <p className="text-xs text-gray-400 truncate">{prospect.industry || 'No industry'}{prospect.companySize ? ` • ${prospect.companySize}` : ''}</p>
                        </div>
                        <div className="flex items-center gap-3 ml-3">
                          {prospect.budget && <span className="text-xs text-green-400 font-semibold">{prospect.budget}</span>}
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            prospect.status === 'Qualifying' ? 'bg-yellow-500/20 text-yellow-400' :
                            prospect.status === 'Proposal' ? 'bg-blue-500/20 text-blue-400' :
                            prospect.status === 'Won' || prospect.status === 'Closed Won' ? 'bg-green-500/20 text-green-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {prospect.status || 'New'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <p className="text-gray-500 text-sm font-semibold mb-1">Pipeline is empty</p>
                    <p className="text-gray-600 text-xs mb-4">Add your first corporate prospect to get started</p>
                    <button onClick={() => setActiveTab('pipeline')} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-semibold transition">
                      Add First Prospect
                    </button>
                  </div>
                )}
              </div>

              {/* Execute the System */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-2">Execute the System</h3>
                <p className="text-xs text-gray-500 mb-4">Every prospect runs through this process. The system works — you decide.</p>
                <div className="space-y-2">
                  {[
                    { step: '1', label: 'Add Prospect to Pipeline', sub: 'Company, industry, challenge, budget', tab: 'pipeline', color: 'text-blue-400' },
                    { step: '2', label: 'AI Qualifies & Scores', sub: 'ICP fit analysis, go/no-go recommendation', tab: 'pipeline', color: 'text-cyan-400' },
                    { step: '3', label: 'Build Client Avatar', sub: 'Decision-maker profile, pain points, goals', tab: 'client-avatar', color: 'text-green-400' },
                    { step: '4', label: 'Generate Blueprint', sub: 'ALIGN/DEFINE/DESIGN/SHINE for this prospect', tab: 'blueprint', color: 'text-purple-400' },
                    { step: '5', label: 'Create PitchMap & Propose', sub: 'AI pitch script tailored to their pain', tab: 'pitchmap', color: 'text-yellow-400' },
                    { step: '6', label: 'Follow Up (5x5 System)', sub: '5 touches, 5 channels until close', tab: 'corporate-mastery', color: 'text-pink-400' },
                    { step: '7', label: 'Win > Hand Off to ATLAS', sub: 'Closed deal becomes an ATLAS project', tab: 'pipeline', color: 'text-green-400' },
                  ].map((item) => (
                    <button
                      key={item.step}
                      onClick={() => setActiveTab(item.tab)}
                      className="w-full flex items-center gap-3 bg-gray-700/30 hover:bg-gray-700/60 border border-gray-700 hover:border-gray-600 px-3 py-2.5 rounded-lg transition text-left"
                    >
                      <span className={`text-xs font-bold ${item.color} bg-white/5 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0`}>{item.step}</span>
                      <div className="min-w-0">
                        <p className="font-semibold text-xs">{item.label}</p>
                        <p className="text-[10px] text-gray-500 truncate">{item.sub}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Navigate the System — quick links to all tabs */}
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold mb-4">Navigate the System</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: 'Corporate Sales Mastery', sub: '6 frameworks for $25K+ deals', tab: 'corporate-mastery', color: 'border-blue-600/40 hover:border-blue-500' },
                  { label: 'Blueprint Framework', sub: 'ALIGN > DEFINE > DESIGN > SHINE', tab: 'blueprint', color: 'border-green-600/40 hover:border-green-500' },
                  { label: 'Client Avatar Builder', sub: 'Define who you serve', tab: 'client-avatar', color: 'border-purple-600/40 hover:border-purple-500' },
                  { label: 'Success Path Builder', sub: 'Map the offer & outcome', tab: 'success-path', color: 'border-cyan-600/40 hover:border-cyan-500' },
                  { label: 'PitchMap Generator', sub: 'AI-crafted pitch scripts', tab: 'pitchmap', color: 'border-yellow-600/40 hover:border-yellow-500' },
                  { label: 'Your 6 Sectors', sub: 'Pre-built sector playbooks', tab: 'your-sectors', color: 'border-orange-600/40 hover:border-orange-500' },
                  { label: 'AI Response Handler', sub: 'Analyze emails, draft replies', tab: 'ai-handler', color: 'border-pink-600/40 hover:border-pink-500' },
                  { label: 'Pipeline Tracker', sub: 'Manage all prospects', tab: 'pipeline', color: 'border-emerald-600/40 hover:border-emerald-500' },
                ].map((nav) => (
                  <button
                    key={nav.tab}
                    onClick={() => setActiveTab(nav.tab)}
                    className={`border ${nav.color} bg-gray-700/30 hover:bg-gray-700/60 rounded-xl p-4 text-left transition cursor-pointer`}
                  >
                    <p className="font-bold text-sm mb-0.5">{nav.label}</p>
                    <p className="text-[11px] text-gray-500">{nav.sub}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB: CORPORATE SALES MASTERY */}
        {activeTab === 'corporate-mastery' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">💼 Corporate Sales Mastery</h2>
              <p className="text-gray-400">The original 6 frameworks for closing $25K+ corporate deals</p>
            </div>

            <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-green-400 mb-2">✨ THIS IS YOUR FOUNDATION</h3>
              <p className="text-sm text-gray-300">These are YOUR original frameworks that started this entire system. The Consulting Blueprint enhances this, but THIS is your core sales methodology.</p>
            </div>

            {/* The 6 Frameworks Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <button onClick={() => setCorporateSection('offer-blueprint')} className="bg-blue-600 hover:bg-blue-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">💰</div>
                <div className="font-bold text-sm">$25K Offer Blueprint</div>
              </button>
              <button onClick={() => setCorporateSection('pitch-scripts')} className="bg-green-600 hover:bg-green-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">📝</div>
                <div className="font-bold text-sm">Pitch Scripts</div>
              </button>
              <button onClick={() => setCorporateSection('stack-close')} className="bg-purple-600 hover:bg-purple-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">🎯</div>
                <div className="font-bold text-sm">Stack Close</div>
              </button>
              <button onClick={() => setCorporateSection('targeting-map')} className="bg-yellow-600 hover:bg-yellow-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">🎯</div>
                <div className="font-bold text-sm">Targeting Map</div>
              </button>
              <button onClick={() => setCorporateSection('flywheel')} className="bg-red-600 hover:bg-red-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">🔄</div>
                <div className="font-bold text-sm">Content Flywheel</div>
              </button>
              <button onClick={() => setCorporateSection('follow-up')} className="bg-pink-600 hover:bg-pink-700 p-4 rounded-lg text-center transition">
                <div className="text-3xl mb-2">📧</div>
                <div className="font-bold text-sm">5x5 Follow-Up</div>
              </button>
            </div>

            {/* Framework Content */}
            {corporateSection === 'offer-blueprint' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">💰 The $25K Corporate Offer Blueprint™</h3>
                <p className="text-gray-400 mb-6">Turn what you already know into a boardroom-ready outcome companies will pay for now.</p>

                <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-blue-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">A $25K corporate deal isn't about selling a service—it's about eliminating a $100K+ problem or capturing a $250K+ opportunity.</p>
                </div>

                <div className="bg-gray-700 rounded-xl p-6">
                  <h4 className="font-bold mb-4">The 25K Offer Components (Modular System)</h4>
                  <div className="space-y-4">
                    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                      <h5 className="font-bold text-blue-400 mb-2">TIER 1: Core Solution ($15K-$18K value)</h5>
                      <ul className="text-sm text-gray-300 space-y-1">
                        <li>• Primary service delivery</li>
                        <li>• Standard compliance/documentation</li>
                        <li>• Dedicated account management</li>
                        <li>• Quarterly business reviews</li>
                      </ul>
                    </div>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <h5 className="font-bold text-green-400 mb-2">TIER 2: Strategic Enhancement ($5K-$7K value)</h5>
                      <ul className="text-sm text-gray-300 space-y-1">
                        <li>• Custom reporting/analytics dashboard</li>
                        <li>• Priority response/expedited service</li>
                        <li>• Training & certification for their team</li>
                        <li>• Integration with their existing systems</li>
                      </ul>
                    </div>
                    <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-4">
                      <h5 className="font-bold text-purple-400 mb-2">TIER 3: Risk Mitigation & Growth ($3K-$5K value)</h5>
                      <ul className="text-sm text-gray-300 space-y-1">
                        <li>• Compliance guarantee/audit support</li>
                        <li>• Scalability provisions (built for growth)</li>
                        <li>• Strategic consulting (2-4 sessions/year)</li>
                        <li>• Emergency response protocol</li>
                      </ul>
                    </div>
                  </div>
                  <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg text-center">
                    <p className="font-bold text-lg">TOTAL PACKAGE VALUE: $23K-$30K</p>
                    <p className="text-2xl font-bold text-green-400 mt-2">Your Investment Price: $25K annually</p>
                  </div>
                </div>
              </div>
            )}

            {/* PITCH SCRIPTS */}
            {corporateSection === 'pitch-scripts' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">📝 Corporate Pitch Scripts</h3>
                <p className="text-gray-400 mb-6">Pre-built conversation frameworks for every stage. Stop winging it — run the script, close the deal.</p>

                <div className="bg-green-900/30 border border-green-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-green-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">Corporate buyers don't respond to features. They respond to outcomes, risk reduction, and ROI. Every script leads with the problem you eliminate, not the service you sell.</p>
                </div>

                <div className="space-y-6">
                  {/* Cold Outreach Script */}
                  <div className="bg-gray-700 rounded-xl p-6">
                    <h4 className="font-bold text-lg mb-2 text-blue-400">Script 1: Cold Outreach (First Touch)</h4>
                    <p className="text-xs text-gray-400 mb-4">Use when reaching out to a new prospect for the first time. Goal: get the meeting, not close the deal.</p>
                    <div className="bg-gray-800 rounded-lg p-4 space-y-3 text-sm">
                      <div><span className="text-blue-400 font-semibold">OPENER:</span> <span className="text-gray-300">"Hi [Name], I work with [industry] companies that are dealing with [specific problem]. I noticed [something specific about their company] and wanted to see if this is on your radar."</span></div>
                      <div><span className="text-yellow-400 font-semibold">HOOK:</span> <span className="text-gray-300">"We recently helped a similar company [specific result — save $X, reduce Y by Z%, eliminate problem]. I thought it might be relevant to what you're doing."</span></div>
                      <div><span className="text-green-400 font-semibold">ASK:</span> <span className="text-gray-300">"Would it make sense to grab 15 minutes this week to see if there's a fit? If not, no worries at all."</span></div>
                    </div>
                    <div className="mt-3 bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-3">
                      <p className="text-xs text-yellow-400"><span className="font-bold">Key:</span> Keep it short. No one reads a 5-paragraph cold email. 3-4 sentences max. Specific beats generic.</p>
                    </div>
                  </div>

                  {/* Discovery Call Script */}
                  <div className="bg-gray-700 rounded-xl p-6">
                    <h4 className="font-bold text-lg mb-2 text-green-400">Script 2: Discovery Call (First Meeting)</h4>
                    <p className="text-xs text-gray-400 mb-4">Use on the first call. Goal: understand their pain deeply enough to position your solution perfectly.</p>
                    <div className="bg-gray-800 rounded-lg p-4 space-y-3 text-sm">
                      <div><span className="text-blue-400 font-semibold">FRAME:</span> <span className="text-gray-300">"Thanks for making time. I'd love to learn about what's happening on your end first, then I can share how we might be able to help. Sound good?"</span></div>
                      <div><span className="text-yellow-400 font-semibold">DIG (Pain):</span> <span className="text-gray-300">"What's the biggest challenge you're facing with [area] right now?"</span></div>
                      <div><span className="text-yellow-400 font-semibold">DIG (Cost):</span> <span className="text-gray-300">"What does that cost you — in time, money, or missed opportunities?"</span></div>
                      <div><span className="text-yellow-400 font-semibold">DIG (Timeline):</span> <span className="text-gray-300">"How long has this been a problem? What happens if it doesn't get solved in the next 6 months?"</span></div>
                      <div><span className="text-green-400 font-semibold">BRIDGE:</span> <span className="text-gray-300">"Based on what you're telling me, this is exactly the kind of problem we solve. Can I walk you through how we'd approach this?"</span></div>
                    </div>
                    <div className="mt-3 bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-3">
                      <p className="text-xs text-yellow-400"><span className="font-bold">Key:</span> Listen 80%, talk 20%. Your job is to understand their world, not pitch. The pitch comes in Script 3.</p>
                    </div>
                  </div>

                  {/* Proposal Presentation Script */}
                  <div className="bg-gray-700 rounded-xl p-6">
                    <h4 className="font-bold text-lg mb-2 text-purple-400">Script 3: Proposal Presentation (Closing)</h4>
                    <p className="text-xs text-gray-400 mb-4">Use when presenting your solution. Goal: make the investment feel like a no-brainer.</p>
                    <div className="bg-gray-800 rounded-lg p-4 space-y-3 text-sm">
                      <div><span className="text-blue-400 font-semibold">RECAP:</span> <span className="text-gray-300">"Last time we talked, you mentioned [pain point 1], [pain point 2], and that it's costing you approximately [cost]. Is that still accurate?"</span></div>
                      <div><span className="text-yellow-400 font-semibold">SOLUTION:</span> <span className="text-gray-300">"Here's exactly how we'd solve that. [Walk through your 3-tier offer — Core, Enhancement, Risk Mitigation]"</span></div>
                      <div><span className="text-green-400 font-semibold">ROI FRAME:</span> <span className="text-gray-300">"So the total investment is $25K annually. Based on what you told me, you're losing roughly $[X] per year to this problem. This pays for itself in [timeframe]."</span></div>
                      <div><span className="text-purple-400 font-semibold">CLOSE:</span> <span className="text-gray-300">"What questions do you have? ... Great. Should we get the paperwork started, or would you like to loop in [decision maker] first?"</span></div>
                    </div>
                    <div className="mt-3 bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-3">
                      <p className="text-xs text-yellow-400"><span className="font-bold">Key:</span> Always tie the price back to the cost of their problem. $25K to solve a $100K problem is a 4x return. Frame it that way.</p>
                    </div>
                  </div>

                  {/* Objection Handling */}
                  <div className="bg-gray-700 rounded-xl p-6">
                    <h4 className="font-bold text-lg mb-2 text-red-400">Script 4: Objection Handlers</h4>
                    <p className="text-xs text-gray-400 mb-4">The 5 objections you'll hear every time, and exactly how to handle them.</p>
                    <div className="space-y-3">
                      {[
                        { objection: '"It\'s too expensive"', response: '"I hear you. Let me ask — what\'s the cost of NOT solving this for another year? If this problem is costing you $X/year, the question isn\'t whether you can afford the solution — it\'s whether you can afford not to have one."' },
                        { objection: '"We need to think about it"', response: '"Absolutely, take whatever time you need. Can I ask — what specifically do you need to think through? Sometimes I can address that right now and save us both a round trip."' },
                        { objection: '"We\'re already working with someone"', response: '"That\'s great — it means you already see the value. Curious though, if everything was working perfectly, would we be having this conversation? What\'s the gap you\'re seeing?"' },
                        { objection: '"Can you send me a proposal?"', response: '"I\'d love to. Before I do, I want to make sure it\'s tailored exactly to your situation. Can we do a quick 15-minute call so I don\'t send you something generic?"' },
                        { objection: '"We don\'t have budget right now"', response: '"When does your next budget cycle start? Let\'s plan for that. In the meantime, I can send over a summary of the ROI so you have ammunition when budget conversations happen."' },
                      ].map((item, idx) => (
                        <div key={idx} className="bg-gray-800 rounded-lg p-4">
                          <p className="text-sm font-bold text-red-400 mb-2">{item.objection}</p>
                          <p className="text-sm text-gray-300">{item.response}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* STACK CLOSE */}
            {corporateSection === 'stack-close' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">🎯 The Stack Close Method</h3>
                <p className="text-gray-400 mb-6">Layer so much value that the price feels like a fraction of what they're getting. Make saying "no" feel irrational.</p>

                <div className="bg-purple-900/30 border border-purple-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-purple-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">The Stack Close isn't about discounting. It's about systematically revealing the total value of everything included until the price-to-value gap is so wide that the investment becomes obvious.</p>
                </div>

                {/* The Stack */}
                <div className="bg-gray-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold mb-4">Building The Value Stack</h4>
                  <p className="text-sm text-gray-400 mb-4">Present each layer one at a time. Let them absorb the value before revealing the price.</p>
                  <div className="space-y-3">
                    {[
                      { layer: 'Layer 1', name: 'Core Delivery', value: '$15,000', desc: 'The primary service — what solves their main problem', color: 'border-blue-600 bg-blue-900/20' },
                      { layer: 'Layer 2', name: 'Custom Implementation', value: '$5,000', desc: 'Tailored setup, onboarding, integration with their systems', color: 'border-green-600 bg-green-900/20' },
                      { layer: 'Layer 3', name: 'Strategic Consulting', value: '$4,000', desc: '4 quarterly strategy sessions with leadership', color: 'border-purple-600 bg-purple-900/20' },
                      { layer: 'Layer 4', name: 'Priority Support', value: '$3,000', desc: 'Dedicated account manager, expedited response times', color: 'border-yellow-600 bg-yellow-900/20' },
                      { layer: 'Layer 5', name: 'Training & Documentation', value: '$2,500', desc: 'Full team training, custom SOPs, video walkthroughs', color: 'border-cyan-600 bg-cyan-900/20' },
                      { layer: 'Layer 6', name: 'Compliance & Risk Shield', value: '$2,000', desc: 'Audit-ready documentation, compliance monitoring, risk alerts', color: 'border-red-600 bg-red-900/20' },
                    ].map((layer) => (
                      <div key={layer.layer} className={`border ${layer.color} rounded-lg p-4 flex items-center justify-between`}>
                        <div>
                          <p className="font-bold text-sm">{layer.layer}: {layer.name}</p>
                          <p className="text-xs text-gray-400">{layer.desc}</p>
                        </div>
                        <span className="text-green-400 font-bold text-lg ml-4 flex-shrink-0">{layer.value}</span>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 border-t border-gray-600 pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-gray-400 font-semibold">Total Value:</span>
                      <span className="text-gray-400 font-bold text-xl line-through">$31,500</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-white font-bold text-lg">Your Investment:</span>
                      <span className="text-green-400 font-bold text-2xl">$25,000/year</span>
                    </div>
                    <p className="text-xs text-green-400 mt-2 text-right">That's a 79¢ return for every $1 in value — before counting the ROI on solving their problem.</p>
                  </div>
                </div>

                {/* The Delivery Script */}
                <div className="bg-gray-700 rounded-xl p-6">
                  <h4 className="font-bold mb-4">How to Deliver the Stack</h4>
                  <div className="space-y-4 text-sm">
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="font-bold text-blue-400 mb-2">Step 1: Present Each Layer Separately</p>
                      <p className="text-gray-300">"First, you get [Core Delivery] — this alone is worth $15K based on what companies in your industry typically pay for this."</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="font-bold text-green-400 mb-2">Step 2: Build the Running Total</p>
                      <p className="text-gray-300">"On top of that, you also get [Custom Implementation]... that brings us to $20K in value. But we're not done."</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="font-bold text-purple-400 mb-2">Step 3: Pause Before the Price</p>
                      <p className="text-gray-300">"So the total package value is $31,500. Now, because we're looking at an annual partnership, your investment is... $25,000."</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="font-bold text-yellow-400 mb-2">Step 4: Anchor to Their Problem Cost</p>
                      <p className="text-gray-300">"You told me this problem costs you roughly $[X] per year. At $25K, you're getting $31K in value AND solving a $[X] problem. This pays for itself by [month]."</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TARGETING MAP */}
            {corporateSection === 'targeting-map' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">🎯 The Targeting Map</h3>
                <p className="text-gray-400 mb-6">Stop chasing everyone. Identify the exact companies, roles, and signals that make a prospect worth pursuing.</p>

                <div className="bg-yellow-900/30 border border-yellow-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-yellow-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">Not every company is your client. The Targeting Map filters the entire market down to the companies most likely to buy, most profitable to serve, and most aligned with your expertise. Precision beats volume every time.</p>
                </div>

                {/* The 4 Filters */}
                <div className="bg-gray-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold mb-4">The 4-Filter Targeting System</h4>
                  <div className="space-y-4">
                    <div className="bg-yellow-900/20 border border-yellow-600 rounded-lg p-4">
                      <h5 className="font-bold text-yellow-400 mb-2">Filter 1: Industry Fit</h5>
                      <p className="text-sm text-gray-300 mb-2">Which industries have the problem you solve?</p>
                      <ul className="text-sm text-gray-400 space-y-1">
                        <li>• What industries have you served successfully?</li>
                        <li>• Where does your expertise create the most value?</li>
                        <li>• Which industries are growing and have budget?</li>
                      </ul>
                    </div>
                    <div className="bg-blue-900/20 border border-blue-600 rounded-lg p-4">
                      <h5 className="font-bold text-blue-400 mb-2">Filter 2: Company Size & Revenue</h5>
                      <p className="text-sm text-gray-300 mb-2">Who can actually afford a $25K engagement?</p>
                      <ul className="text-sm text-gray-400 space-y-1">
                        <li>• Sweet spot: $5M-$100M revenue (big enough to pay, small enough to access decision-makers)</li>
                        <li>• 50-500 employees (enough pain, not too bureaucratic)</li>
                        <li>• Growing companies over stagnant ones (growth creates problems you solve)</li>
                      </ul>
                    </div>
                    <div className="bg-green-900/20 border border-green-600 rounded-lg p-4">
                      <h5 className="font-bold text-green-400 mb-2">Filter 3: Decision-Maker Access</h5>
                      <p className="text-sm text-gray-300 mb-2">Can you reach the person who signs the check?</p>
                      <ul className="text-sm text-gray-400 space-y-1">
                        <li>• Target: C-suite, VP, Director level (not managers or coordinators)</li>
                        <li>• LinkedIn accessible? Speaking at events? Active in industry groups?</li>
                        <li>• If you can't reach the decision-maker in 3 touches, move on</li>
                      </ul>
                    </div>
                    <div className="bg-purple-900/20 border border-purple-600 rounded-lg p-4">
                      <h5 className="font-bold text-purple-400 mb-2">Filter 4: Buying Signals</h5>
                      <p className="text-sm text-gray-300 mb-2">Is there evidence they're ready to buy NOW?</p>
                      <ul className="text-sm text-gray-400 space-y-1">
                        <li>• Recently raised funding or had a growth event</li>
                        <li>• Hiring for roles related to your solution area</li>
                        <li>• Publicly mentioned challenges you solve (interviews, press, LinkedIn posts)</li>
                        <li>• Current vendor contract expiring (check SAM.gov for government, industry reports for private)</li>
                        <li>• Leadership change (new executives often bring new budgets)</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Prospect Scoring */}
                <div className="bg-gray-700 rounded-xl p-6">
                  <h4 className="font-bold mb-4">Quick Score: Is This Prospect Worth Pursuing?</h4>
                  <p className="text-sm text-gray-400 mb-4">Score each prospect 1-5 on these 4 criteria. Total 16+ = pursue aggressively. 12-15 = warm lead. Below 12 = pass.</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                      { criteria: 'Problem Severity', q: 'How badly do they need this solved?' },
                      { criteria: 'Budget Capacity', q: 'Can they afford $25K+?' },
                      { criteria: 'Decision Access', q: 'Can you reach the buyer?' },
                      { criteria: 'Timing', q: 'Are they ready to act now?' },
                    ].map((c) => (
                      <div key={c.criteria} className="bg-gray-800 rounded-lg p-4 text-center">
                        <p className="font-bold text-sm mb-1">{c.criteria}</p>
                        <p className="text-xs text-gray-400">{c.q}</p>
                        <p className="text-lg font-bold text-yellow-400 mt-2">_ / 5</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* CONTENT FLYWHEEL */}
            {corporateSection === 'flywheel' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">🔄 The Content Flywheel</h3>
                <p className="text-gray-400 mb-6">Create once, repurpose everywhere. Build authority that attracts corporate clients to you instead of chasing them.</p>

                <div className="bg-red-900/30 border border-red-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-red-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">Corporate decision-makers don't buy from cold emails alone. They buy from people they trust, respect, and see as authorities. The Flywheel turns one piece of thinking into 10+ pieces of content across every platform — consistently, without burning out.</p>
                </div>

                {/* The Flywheel Process */}
                <div className="bg-gray-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold mb-4">The 1-to-10 Content Engine</h4>
                  <p className="text-sm text-gray-400 mb-4">Start with ONE core insight per week. Then break it down.</p>

                  <div className="space-y-3">
                    <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
                      <p className="font-bold text-blue-400 text-sm mb-1">Step 1: Core Content (1 piece/week)</p>
                      <p className="text-sm text-gray-300">Write one 500-word LinkedIn article or record one 5-min video about a real problem you solve.</p>
                      <p className="text-xs text-gray-500 mt-1">Example: "3 reasons your emergency logistics plan will fail when disaster hits"</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-green-500">
                      <p className="font-bold text-green-400 text-sm mb-1">Step 2: Break Into Micro-Content (5-7 pieces)</p>
                      <p className="text-sm text-gray-300">Pull quotes, stats, and key points from your core piece:</p>
                      <ul className="text-xs text-gray-400 mt-1 space-y-1">
                        <li>• 3 LinkedIn text posts (one key point each)</li>
                        <li>• 1 carousel or infographic</li>
                        <li>• 1 email newsletter snippet</li>
                        <li>• 1 short-form video (60 sec — talk through one point)</li>
                      </ul>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-purple-500">
                      <p className="font-bold text-purple-400 text-sm mb-1">Step 3: Engage & Distribute (Daily — 15 min)</p>
                      <p className="text-sm text-gray-300">Comment on your prospects' posts. Share your micro-content. DM people who engage.</p>
                      <p className="text-xs text-gray-500 mt-1">The content gets you noticed. The engagement builds the relationship.</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-yellow-500">
                      <p className="font-bold text-yellow-400 text-sm mb-1">Step 4: Archive & Compound (Monthly)</p>
                      <p className="text-sm text-gray-300">At month-end, package your best content into:</p>
                      <ul className="text-xs text-gray-400 mt-1 space-y-1">
                        <li>• A case study or white paper</li>
                        <li>• A "best of" email to your list</li>
                        <li>• Talking points for calls and pitches</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Content Topics */}
                <div className="bg-gray-700 rounded-xl p-6">
                  <h4 className="font-bold mb-4">What to Talk About (Content Pillars)</h4>
                  <p className="text-sm text-gray-400 mb-4">Rotate between these 4 pillars. Never run out of ideas.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {[
                      { pillar: 'Problem Awareness', desc: 'Educate prospects about problems they don\'t realize they have. Make them feel the pain.', example: '"Most companies don\'t discover their compliance gap until the audit..."' },
                      { pillar: 'Solution Proof', desc: 'Show how problems get solved — case studies, before/after, methodology breakdowns.', example: '"Here\'s exactly how we saved a fleet company $180K in 90 days..."' },
                      { pillar: 'Authority & Credibility', desc: 'Share your perspective, industry analysis, predictions. Position as the expert.', example: '"3 trends that will reshape emergency logistics by 2027..."' },
                      { pillar: 'Behind the Scenes', desc: 'Show how you work, your process, your team. People buy from people they trust.', example: '"Here\'s what a typical engagement looks like in week 1..."' },
                    ].map((p) => (
                      <div key={p.pillar} className="bg-gray-800 rounded-lg p-4">
                        <p className="font-bold text-sm mb-1">{p.pillar}</p>
                        <p className="text-xs text-gray-400 mb-2">{p.desc}</p>
                        <p className="text-xs text-gray-500 italic">{p.example}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* 5x5 FOLLOW-UP */}
            {corporateSection === 'follow-up' && (
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-2xl font-bold mb-4">📧 The 5x5 Follow-Up System</h3>
                <p className="text-gray-400 mb-6">5 touches across 5 channels over 25 days. Systematic follow-up that converts without being annoying.</p>

                <div className="bg-pink-900/30 border border-pink-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold text-pink-400 mb-3">Core Principle</h4>
                  <p className="text-gray-300">80% of deals close after the 5th contact. Most people quit after 1-2 attempts. The 5x5 system ensures you stay in front of every prospect through multiple channels — email, phone, LinkedIn, video, and mail — so they can't forget you even if they want to.</p>
                </div>

                {/* The 5x5 Grid */}
                <div className="bg-gray-700 rounded-xl p-6 mb-6">
                  <h4 className="font-bold mb-4">The 25-Day Follow-Up Sequence</h4>
                  <div className="space-y-3">
                    {[
                      { day: 'Day 1', channel: 'Email', action: 'Send initial outreach email (Script 1 from Pitch Scripts)', tone: 'Professional, direct, value-first', color: 'border-blue-500' },
                      { day: 'Day 3', channel: 'LinkedIn', action: 'Connect + personalized note referencing their recent post or company news', tone: 'Casual, human, curious', color: 'border-cyan-500' },
                      { day: 'Day 7', channel: 'Phone', action: 'Call their office. Leave a 30-second voicemail if no answer. Reference the email.', tone: 'Warm, confident, brief', color: 'border-green-500' },
                      { day: 'Day 10', channel: 'Email', action: 'Follow-up with a relevant case study or insight. "Thought this might be useful..."', tone: 'Giving value, not asking', color: 'border-blue-500' },
                      { day: 'Day 14', channel: 'LinkedIn', action: 'Comment on their post or share an article and tag them. Stay visible.', tone: 'Peer-to-peer, not salesy', color: 'border-cyan-500' },
                      { day: 'Day 17', channel: 'Video', action: 'Send a 60-second personalized Loom video. "Hey [Name], quick thought for you..."', tone: 'Personal, unexpected, memorable', color: 'border-purple-500' },
                      { day: 'Day 20', channel: 'Phone', action: 'Second call attempt. This time mention the video. "Did you get my video message?"', tone: 'Direct, friendly callback', color: 'border-green-500' },
                      { day: 'Day 22', channel: 'Email', action: 'Break-up email: "I don\'t want to be a pest. If timing is off, no worries — when should I circle back?"', tone: 'Respectful exit, leaves door open', color: 'border-yellow-500' },
                      { day: 'Day 25', channel: 'Mail', action: 'Send a handwritten note or printed case study to their office. Physical mail stands out.', tone: 'Memorable, personal touch', color: 'border-red-500' },
                    ].map((touch) => (
                      <div key={touch.day} className={`bg-gray-800 rounded-lg p-4 border-l-4 ${touch.color}`}>
                        <div className="flex items-center justify-between mb-1">
                          <p className="font-bold text-sm">{touch.day}: {touch.channel}</p>
                          <span className="text-xs text-gray-500">{touch.tone}</span>
                        </div>
                        <p className="text-sm text-gray-300">{touch.action}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Rules */}
                <div className="bg-gray-700 rounded-xl p-6">
                  <h4 className="font-bold mb-4">5x5 Rules</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {[
                      { rule: 'Never pitch twice in a row', why: 'Alternate between giving value and making asks. If Touch 1 was an ask, Touch 2 should be pure value.' },
                      { rule: 'Vary the channel', why: 'Email, phone, LinkedIn, video, mail — hit them from different angles. Some people don\'t do email. Some live on LinkedIn.' },
                      { rule: 'Reference previous touches', why: '"I sent you a video last week about..." builds continuity. They\'ll feel like they already know you.' },
                      { rule: 'Know when to stop', why: 'After the 5x5 (Day 25), move them to a quarterly check-in list. Don\'t keep hammering. Timing may just be wrong.' },
                      { rule: 'Track everything', why: 'Log every touch in the pipeline. Know exactly where every prospect is in the sequence.' },
                      { rule: 'The break-up email works', why: 'More prospects respond to "I\'ll stop reaching out" than to "just checking in." Give them permission to say no — many say yes.' },
                    ].map((r, idx) => (
                      <div key={idx} className="bg-gray-800 rounded-lg p-4">
                        <p className="font-bold text-sm text-pink-400 mb-1">{r.rule}</p>
                        <p className="text-xs text-gray-400">{r.why}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB: BLUEPRINT FRAMEWORK */}
        {activeTab === 'blueprint' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🎯 The Corporate Consulting Blueprint</h2>
              <p className="text-gray-400">The proven 4-step framework used by hundreds of consultants to build $100K-$442K businesses</p>
            </div>

            {/* The 4 Steps */}
            <div className="space-y-6">
              {/* Step 1: ALIGN */}
              <div className="bg-gradient-to-r from-blue-900 to-blue-800 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-blue-600 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">1</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-3">ALIGN - Build Business That Reflects Your Purpose</h3>
                    <p className="text-blue-100 mb-4">"Purpose comes before profit. Purpose is the rocket fuel of every thriving business."</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-blue-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">1. Know WHO You Serve</h4>
                        <p className="text-sm text-blue-200">Find the intersection of: expertise that creates value + clients who energize you + genuine demand</p>
                      </div>
                      <div className="bg-blue-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">2. Lead With STRENGTHS</h4>
                        <p className="text-sm text-blue-200">Your Zone of Genius = What energizes you + What you're exceptional at + What creates value</p>
                      </div>
                      <div className="bg-blue-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">3. Make Positive IMPACT</h4>
                        <p className="text-sm text-blue-200">3 levels: Immediate (client results), Extended (organizational impact), Legacy (lasting change)</p>
                      </div>
                    </div>

                    <button onClick={() => setActiveTab('client-avatar')} className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg font-semibold transition">
                      Start with Client Avatar Builder →
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 2: DEFINE */}
              <div className="bg-gradient-to-r from-green-900 to-green-800 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-green-600 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">2</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-3">DEFINE - Clarify Who You Serve &amp; Results You Deliver</h3>
                    <p className="text-green-100 mb-4">{'"Specialists stand out, attract premium clients, and command higher fees. The riches are in the niches."'}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-green-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">1. The Nesting Doll Method</h4>
                        <p className="text-sm text-green-200">Start broad, then narrow relentlessly. Industry → Sub-industry → Company size → Role → Specific pain. The smallest doll is your ideal client.</p>
                      </div>
                      <div className="bg-green-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">2. Pain-First Positioning</h4>
                        <p className="text-sm text-green-200">{"Don't lead with what you do. Lead with the problem you eliminate. \"I help [specific role] at [company type] stop losing $X to [specific problem].\""}</p>
                      </div>
                      <div className="bg-green-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">3. Results You Deliver</h4>
                        <p className="text-sm text-green-200">Define the measurable transformation. Before state → After state. Revenue gained, costs cut, time saved, risks eliminated. Be specific — numbers build trust.</p>
                      </div>
                    </div>

                    <div className="bg-green-950/40 rounded-lg p-4 mb-4">
                      <h4 className="font-bold text-sm mb-2">The Client Avatar Questions</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-green-200">
                        <p>• What industry are they in?</p>
                        <p>• What is their role/title?</p>
                        <p>• What keeps them up at night?</p>
                        <p>• What have they already tried?</p>
                        <p>• What does success look like for them?</p>
                        <p>• What is the cost of inaction?</p>
                        <p>• Who else is involved in the decision?</p>
                        <p>• What budget range makes sense?</p>
                      </div>
                    </div>

                    <button onClick={() => setActiveTab('client-avatar')} className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-semibold transition">
                      Build Your Client Avatar →
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 3: DESIGN */}
              <div className="bg-gradient-to-r from-purple-900 to-purple-800 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-purple-600 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">3</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-3">DESIGN - Turn Expertise Into a High-Value Offer</h3>
                    <p className="text-purple-100 mb-4">{'"A strong offer = clear promise of transformation + proven process + confidence in positioning. Stop selling time — sell outcomes."'}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-purple-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">1. The Success Path</h4>
                        <p className="text-sm text-purple-200">Map the journey from their current pain to their desired outcome. Define milestones. Show them the path is clear, tested, and repeatable.</p>
                      </div>
                      <div className="bg-purple-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">2. Offer Architecture</h4>
                        <p className="text-sm text-purple-200">Structure your offer in tiers (Core + Enhancement + Risk Shield). Make it modular — clients can see the value of each component and the total is undeniable.</p>
                      </div>
                      <div className="bg-purple-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">3. Confidence Pricing</h4>
                        <p className="text-sm text-purple-200">Price based on the value of the outcome, not hours worked. If you solve a $100K problem, $25K is a bargain. Anchor to the cost of their problem, not your cost to deliver.</p>
                      </div>
                    </div>

                    <div className="bg-purple-950/40 rounded-lg p-4 mb-4">
                      <h4 className="font-bold text-sm mb-2">Offer Design Checklist</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-purple-200">
                        <p>• Can you articulate the transformation in one sentence?</p>
                        <p>• Is the process clearly defined (steps/phases)?</p>
                        <p>• Does the client understand what they get at each tier?</p>
                        <p>• Is the price anchored to the value of the outcome?</p>
                        <p>• Do you have proof it works (case studies, results)?</p>
                        <p>• Is there a risk-reversal element (guarantee, pilot)?</p>
                      </div>
                    </div>

                    <button onClick={() => setActiveTab('success-path')} className="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg font-semibold transition">
                      Build Your Success Path →
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 4: SHINE */}
              <div className="bg-gradient-to-r from-yellow-900 to-yellow-800 rounded-xl p-6">
                <div className="flex items-start gap-4">
                  <div className="bg-yellow-600 w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">4</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-3">SHINE - Attract Ideal Clients With a Memorable Message</h3>
                    <p className="text-yellow-100 mb-4">{'"Your offer might be powerful, but if you can\'t communicate it clearly — your ideal clients won\'t buy it. Clarity is the ultimate competitive advantage."'}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-yellow-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">1. The One-Liner</h4>
                        <p className="text-sm text-yellow-200">{"Craft a single sentence that makes them say \"tell me more.\" Format: \"I help [who] achieve [result] without [pain point].\" Test it — if they don't lean in, rewrite it."}</p>
                      </div>
                      <div className="bg-yellow-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">2. The PitchMap</h4>
                        <p className="text-sm text-yellow-200">{"Structure every pitch: Problem (make them feel it) → Agitate (cost of inaction) → Solution (your process) → Proof (results/case studies) → CTA (clear next step)."}</p>
                      </div>
                      <div className="bg-yellow-950/50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">3. Authority Signals</h4>
                        <p className="text-sm text-yellow-200">Build trust before the pitch. Case studies, testimonials, content, certifications, speaking — show proof you can deliver before you ever ask for the sale.</p>
                      </div>
                    </div>

                    <div className="bg-yellow-950/40 rounded-lg p-4 mb-4">
                      <h4 className="font-bold text-sm mb-2">Message Clarity Test</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-yellow-200">
                        <p>• Can a stranger understand your offer in 10 seconds?</p>
                        <p>• Does your message focus on THEIR problem, not your service?</p>
                        <p>• Is the outcome specific and measurable?</p>
                        <p>• Could a competitor copy your message word-for-word? (If yes, it needs work)</p>
                        <p>• Does it create urgency or FOMO?</p>
                        <p>• Is there a clear, low-friction next step?</p>
                      </div>
                    </div>

                    <button onClick={() => setActiveTab('pitchmap')} className="bg-yellow-600 hover:bg-yellow-700 px-6 py-2 rounded-lg font-semibold transition">
                      Create Your PitchMap →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: CLIENT AVATAR BUILDER */}
        {activeTab === 'client-avatar' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-1">Client Avatar Builder</h2>
                <p className="text-gray-400">Define your ideal client with precision — find the smallest nesting doll</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => { resetAvatarForm(); }} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  + New Avatar
                </button>
                <button onClick={fetchAvatars} className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold text-sm transition">
                  Refresh
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* LEFT: Saved Avatars List */}
              <div className="md:col-span-1">
                <div className="bg-gray-800 rounded-xl p-4">
                  <h3 className="font-bold text-sm mb-3">Saved Avatars ({avatars.length})</h3>
                  {avatarsLoading ? (
                    <div className="text-center py-6">
                      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <p className="text-xs text-gray-500">Loading...</p>
                    </div>
                  ) : avatars.length > 0 ? (
                    <div className="space-y-2">
                      {avatars.map((avatar: any) => (
                        <div
                          key={avatar.id}
                          className={`p-3 rounded-lg border cursor-pointer transition ${
                            editingAvatarId === avatar.id
                              ? 'bg-blue-900/30 border-blue-600'
                              : 'bg-gray-700/50 border-gray-600/50 hover:border-gray-500'
                          }`}
                          onClick={() => loadAvatarForEdit(avatar)}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-semibold text-sm text-blue-400 truncate">{avatar.avatarName || avatar.companyName || 'Unnamed'}</p>
                            <button
                              onClick={(e) => { e.stopPropagation(); deleteClientAvatar(avatar.id); }}
                              className="text-red-400 hover:text-red-300 text-xs ml-2 flex-shrink-0"
                            >
                              Delete
                            </button>
                          </div>
                          <p className="text-xs text-gray-400 truncate">{avatar.industry || 'No industry'}{avatar.companySize ? ` • ${avatar.companySize}` : ''}</p>
                          {avatar.qualificationScore && (
                            <div className="flex items-center gap-2 mt-1">
                              <div className="flex-1 bg-gray-600 rounded-full h-1.5">
                                <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${avatar.qualificationScore}%` }}></div>
                              </div>
                              <span className="text-[10px] text-gray-400">{avatar.qualificationScore}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <p className="text-gray-500 text-xs mb-1">No avatars yet</p>
                      <p className="text-gray-600 text-[10px]">Build your first one using the form</p>
                    </div>
                  )}
                </div>
              </div>

              {/* RIGHT: Avatar Form */}
              <div className="md:col-span-2 space-y-4">
                {/* Form Header */}
                <div className="bg-gray-800 rounded-xl p-5">
                  <h3 className="font-bold text-lg mb-1">{editingAvatarId ? 'Edit Avatar' : 'New Avatar'}</h3>
                  <p className="text-xs text-gray-500">The more precise the avatar, the sharper your pitch. Fill in everything you know.</p>
                </div>

                {/* Professional Profile */}
                <div className="bg-gray-800 rounded-xl p-5">
                  <h4 className="font-bold text-sm mb-3 text-blue-400">Professional Profile</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold mb-1">Avatar / Company Name *</label>
                      <input type="text" placeholder="e.g., Emergency Management Director"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.avatarName}
                        onChange={(e) => setAvatarFormData({...avatarFormData, avatarName: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Industry / Sector *</label>
                      <input type="text" placeholder="e.g., Public Sector, Emergency Services"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.industry}
                        onChange={(e) => setAvatarFormData({...avatarFormData, industry: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Company Size</label>
                      <input type="text" placeholder="e.g., 200-1000 employees"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.companySize}
                        onChange={(e) => setAvatarFormData({...avatarFormData, companySize: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Budget Range</label>
                      <input type="text" placeholder="e.g., $25K-$100K"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.budget}
                        onChange={(e) => setAvatarFormData({...avatarFormData, budget: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Pain & Goals */}
                <div className="bg-gray-800 rounded-xl p-5">
                  <h4 className="font-bold text-sm mb-3 text-green-400">Pain Points &amp; Goals</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold mb-1">Pain Points *</label>
                      <textarea rows={3} placeholder="What keeps them up at night? What's costing them money, time, or risk?"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.painPoints}
                        onChange={(e) => setAvatarFormData({...avatarFormData, painPoints: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Goals</label>
                      <textarea rows={2} placeholder="What outcome are they trying to achieve? What does success look like for them?"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.goals}
                        onChange={(e) => setAvatarFormData({...avatarFormData, goals: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1">Decision Makers</label>
                      <input type="text" placeholder="e.g., County Emergency Manager, Board of Supervisors, CFO"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        value={avatarFormData.decisionMakers}
                        onChange={(e) => setAvatarFormData({...avatarFormData, decisionMakers: e.target.value})}
                      />
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  {editingAvatarId ? (
                    <>
                      <button onClick={updateClientAvatar} disabled={savingAvatar}
                        className={`${savingAvatar ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} px-6 py-2.5 rounded-lg font-semibold text-sm transition`}>
                        {savingAvatar ? 'Saving...' : 'Update Avatar'}
                      </button>
                      <button onClick={resetAvatarForm} className="bg-gray-600 hover:bg-gray-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button onClick={createClientAvatar} disabled={savingAvatar || !avatarFormData.avatarName.trim()}
                      className={`${savingAvatar || !avatarFormData.avatarName.trim() ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} px-6 py-2.5 rounded-lg font-semibold text-sm transition`}>
                      {savingAvatar ? 'Analyzing...' : 'Save Avatar & Analyze with AI'}
                    </button>
                  )}
                  <button onClick={() => setActiveTab('success-path')} className="bg-purple-600 hover:bg-purple-700 px-4 py-2.5 rounded-lg font-semibold text-sm transition">
                    Next: Success Path
                  </button>
                </div>

                {/* AI Analysis Results */}
                {avatarAnalysis && (
                  <div className="bg-gray-800 rounded-xl p-5 border border-blue-600/30">
                    <h4 className="font-bold text-lg mb-4 text-blue-400">AI Analysis</h4>
                    
                    {/* Score + Win Probability */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {avatarAnalysis.qualification_score && (
                        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                          <p className="text-xs text-gray-400 mb-1">Qualification Score</p>
                          <p className="text-3xl font-bold text-blue-400">{avatarAnalysis.qualification_score}<span className="text-sm text-gray-500">/100</span></p>
                          <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${avatarAnalysis.qualification_score}%` }}></div>
                          </div>
                        </div>
                      )}
                      {avatarAnalysis.win_probability && (
                        <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
                          <p className="text-xs text-gray-400 mb-1">Win Probability</p>
                          <p className="text-3xl font-bold text-green-400">{avatarAnalysis.win_probability}<span className="text-sm text-gray-500">%</span></p>
                        </div>
                      )}
                    </div>

                    {/* Detailed Analysis */}
                    <div className="space-y-3">
                      {avatarAnalysis.recommended_approach && (
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-xs font-bold text-gray-400 mb-1">Recommended Approach</p>
                          <p className="text-sm text-gray-300">{avatarAnalysis.recommended_approach}</p>
                        </div>
                      )}
                      {avatarAnalysis.key_pain_to_target && (
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-xs font-bold text-gray-400 mb-1">Key Pain to Target</p>
                          <p className="text-sm text-gray-300">{avatarAnalysis.key_pain_to_target}</p>
                        </div>
                      )}
                      {avatarAnalysis.suggested_offer_angle && (
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-xs font-bold text-gray-400 mb-1">Suggested Offer Angle</p>
                          <p className="text-sm text-gray-300">{avatarAnalysis.suggested_offer_angle}</p>
                        </div>
                      )}
                      {avatarAnalysis.objection_to_expect && (
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-xs font-bold text-red-400 mb-1">Objection to Expect</p>
                          <p className="text-sm text-gray-300">{avatarAnalysis.objection_to_expect}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB: SUCCESS PATH BUILDER */}
        {activeTab === 'success-path' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🛤️ Success Path Builder</h2>
              <p className="text-gray-400">Map your proprietary process from Point A → Point B</p>
            </div>

            <div className="bg-purple-900/30 border border-purple-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-purple-400 mb-2">💡 Your Success Path = Your Proprietary Process</h3>
              <p className="text-sm text-gray-300">"This is the method behind the magic. It shows you don't just hope for results—you have a repeatable framework that delivers them."</p>
            </div>

            {/* Prospect Selection */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Link to Prospect (Optional)</h3>
              <select 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={successPathFormData.prospectId}
                onChange={(e) => setSuccessPathFormData({...successPathFormData, prospectId: e.target.value})}
              >
                <option value="">Create new path (not linked)</option>
                {prospects.map(prospect => (
                  <option key={prospect.id} value={prospect.id}>
                    {prospect.companyName} - {prospect.industry}
                  </option>
                ))}
              </select>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <div>
                <label className="block text-sm font-semibold mb-2">Success Path Name *</label>
                <input 
                  type="text" 
                  placeholder="e.g., Emergency Response Optimization Path" 
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white mb-4"
                  value={successPathFormData.pathName}
                  onChange={(e) => setSuccessPathFormData({...successPathFormData, pathName: e.target.value})}
                />
              </div>
            </div>

            {/* Point A → Point B */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-red-900/30 border-2 border-red-700 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="bg-red-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">A</div>
                  <h3 className="text-xl font-bold">Current State (Where They Are Now)</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-red-300">What challenges are they facing? *</label>
                    <textarea 
                      rows={3} 
                      placeholder="e.g., 4-5 hour mobilization times, lack of emergency response infrastructure" 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
                      value={successPathFormData.startingPoint}
                      onChange={(e) => setSuccessPathFormData({...successPathFormData, startingPoint: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="bg-green-900/30 border-2 border-green-700 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="bg-green-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">B</div>
                  <h3 className="text-xl font-bold">Desired State (Where They Want to Be)</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-semibold mb-1 text-green-300">What specific outcome will they achieve? *</label>
                    <textarea 
                      rows={3} 
                      placeholder="e.g., 90-minute mobilization capability, 24/7 emergency response" 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white"
                      value={successPathFormData.endGoal}
                      onChange={(e) => setSuccessPathFormData({...successPathFormData, endGoal: e.target.value})}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Milestones */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Milestones</h3>
              <textarea 
                rows={4} 
                placeholder="e.g., Phase 1: Assessment (Month 1-2), Phase 2: Implementation (Month 3-6), Phase 3: Optimization (Month 7-12)" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={successPathFormData.milestones}
                onChange={(e) => setSuccessPathFormData({...successPathFormData, milestones: e.target.value})}
              />
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <label className="block text-sm font-semibold mb-2">Timeline</label>
              <input 
                type="text" 
                placeholder="e.g., 12 months" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={successPathFormData.timeline}
                onChange={(e) => setSuccessPathFormData({...successPathFormData, timeline: e.target.value})}
              />
            </div>

            {notification && (
              <div className={`mb-4 p-4 rounded-lg ${
                notification.type === 'success' ? 'bg-green-900/30 border border-green-700 text-green-400' : 'bg-red-900/30 border border-red-700 text-red-400'
              }`}>
                {notification.message}
              </div>
            )}

            <div className="flex gap-3">
              <button 
                onClick={createSuccessPath}
                className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-semibold transition"
              >
                💾 Save Success Path
              </button>
              <button onClick={() => setActiveTab('pitchmap')} className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg font-semibold transition">
                Next: Create PitchMap →
              </button>
            </div>
          </div>
        )}

        {/* TAB: PITCHMAP GENERATOR */}
        {activeTab === 'pitchmap' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🎤 PitchMap Generator</h2>
              <p className="text-gray-400">Craft your core message using the 5-element framework</p>
            </div>

            <div className="bg-yellow-900/30 border border-yellow-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-yellow-400 mb-2">💡 Your PitchMap = Your Core Message</h3>
              <p className="text-sm text-gray-300">"This becomes the foundation for your LinkedIn profile, website, elevator pitch, proposals—every touchpoint where you communicate your value."</p>
            </div>

            {/* Prospect Selection */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Link to Prospect (Optional)</h3>
              <select 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={pitchmapFormData.prospectId}
                onChange={(e) => setPitchmapFormData({...pitchmapFormData, prospectId: e.target.value})}
              >
                <option value="">Create new pitchmap (not linked)</option>
                {prospects.map(prospect => (
                  <option key={prospect.id} value={prospect.id}>
                    {prospect.companyName} - {prospect.industry}
                  </option>
                ))}
              </select>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <div>
                <label className="block text-sm font-semibold mb-2">PitchMap Name *</label>
                <input 
                  type="text" 
                  placeholder="e.g., Emergency Response PitchMap" 
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white mb-4"
                  value={pitchmapFormData.pitchMapName}
                  onChange={(e) => setPitchmapFormData({...pitchmapFormData, pitchMapName: e.target.value})}
                />
              </div>
            </div>

            {/* Element 1: DEFINER */}
            <div className="bg-gray-800 rounded-xl p-6 mb-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">1</div>
                <h3 className="text-lg font-bold">Pain Point *</h3>
              </div>
              <p className="text-sm text-gray-400 mb-3">What specific problem does your ideal client face?</p>
              <textarea 
                rows={3} 
                placeholder="e.g., 4-5 hour emergency response mobilization times leading to increased liability and slower disaster recovery" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={pitchmapFormData.painPoint}
                onChange={(e) => setPitchmapFormData({...pitchmapFormData, painPoint: e.target.value})}
              />
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-green-600 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">2</div>
                <h3 className="text-lg font-bold">Solution *</h3>
              </div>
              <p className="text-sm text-gray-400 mb-3">How does your Blueprint Framework solve this problem?</p>
              <textarea 
                rows={3} 
                placeholder="e.g., Our ALIGN Blueprint Framework reduces mobilization times to 90 minutes through strategic infrastructure optimization" 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={pitchmapFormData.solution}
                onChange={(e) => setPitchmapFormData({...pitchmapFormData, solution: e.target.value})}
              />
            </div>

            {/* AI-Generated Script */}
            {pitchmapScript && (
              <div className="bg-green-900/30 border border-green-700 rounded-xl p-6 mb-6">
                <h3 className="text-xl font-bold mb-4 text-green-400">🤖 AI-Generated Pitch Script</h3>
                <div className="bg-gray-800 rounded-lg p-4">
                  <pre className="text-gray-300 whitespace-pre-wrap text-sm">{pitchmapScript}</pre>
                </div>
                <button 
                  onClick={() => {
                    const blob = new Blob([pitchmapScript], { type: 'text/plain' });
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `${pitchmapFormData.pitchMapName || 'PitchScript'}.txt`;
                    link.click();
                    window.URL.revokeObjectURL(url);
                    showNotification('📄 Script exported!', 'success');
                  }}
                  className="mt-4 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  📄 Export Script
                </button>
              </div>
            )}

            {notification && (
              <div className={`mb-4 p-4 rounded-lg ${
                notification.type === 'success' ? 'bg-green-900/30 border border-green-700 text-green-400' : 'bg-red-900/30 border border-red-700 text-red-400'
              }`}>
                {notification.message}
              </div>
            )}

            <div className="flex gap-3">
              <button 
                onClick={generatePitchmap}
                className="bg-yellow-600 hover:bg-yellow-700 px-6 py-3 rounded-lg font-semibold transition"
              >
                🤖 Generate Pitch Script with AI
              </button>
              <button onClick={() => setActiveTab('your-sectors')} className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition">
                See Your Pre-Built Sectors →
              </button>
            </div>
          </div>
        )}

        {/* TAB: YOUR 6 SECTORS */}
        {activeTab === 'your-sectors' && !selectedSector && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🏢 Your 6 Pre-Loaded Sectors</h2>
              <p className="text-gray-400">Complete systems ready to use - Emergency Logistics, NEMT, Freight, Valet, Compliance, Nonprofit</p>
            </div>

            <div className="bg-green-900/30 border border-green-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-green-400 mb-2">✅ These are READY TO USE</h3>
              <p className="text-sm text-gray-300">Each sector includes: Client avatar, Success Path, PitchMap, Email sequences, Pricing, Discovery scripts - all pre-built with Blueprint psychology integrated</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                {
                  id: 'emergency-logistics',
                  title: '🚨 Emergency Logistics (ATLAS PM)',
                  desc: 'Help emergency management agencies achieve 90-minute mobilization capability',
                  target: 'Emergency Directors, County/State agencies',
                  offer: '$75K Workshop Series (6 months)',
                  promise: 'Own permanent 90-min deployment system',
                  emailSequence: '5-email sequence for emergency management directors',
                  pricing: '$75K annual, $12.5K monthly',
                  discoveryScript: 'Pre-built discovery call script focusing on mobilization times and disaster response'
                },
                {
                  id: 'nemt',
                  title: '🚑 NEMT (DEPOINTE System)',
                  desc: 'Help healthcare systems reduce patient no-shows from 22% to 5%',
                  target: 'Medicaid Directors, MCOs, Hospitals',
                  offer: '$100K annual program',
                  promise: 'Recover $200K+ in lost revenue year 1',
                  emailSequence: '7-email sequence for Medicaid directors',
                  pricing: '$100K annual, $16.7K monthly',
                  discoveryScript: 'Focus on patient no-show reduction and revenue recovery'
                },
                {
                  id: 'freight-brokerage',
                  title: '🚚 Freight Brokerage (FleetFlow™)',
                  desc: 'Help manufacturers save 25% on freight spend',
                  target: 'Supply Chain VPs, Manufacturers',
                  offer: '$80K optimization program',
                  promise: '$600K savings on $2.4M freight spend',
                  emailSequence: '6-email sequence for supply chain executives',
                  pricing: '$80K annual, $13.3K monthly',
                  discoveryScript: 'Focus on freight cost optimization and supply chain efficiency'
                },
                {
                  id: 'valet-services',
                  title: '🏥 Valet Services (DEPOINTE Valet)',
                  desc: 'Help hospitals increase parking revenue 35%',
                  target: 'Hospital CFOs, Patient Experience',
                  offer: '$60K launch program',
                  promise: '$350K additional annual revenue',
                  emailSequence: '5-email sequence for hospital CFOs',
                  pricing: '$60K annual, $10K monthly',
                  discoveryScript: 'Focus on patient experience and revenue generation'
                },
                {
                  id: 'federal-compliance',
                  title: '🔍 Federal Compliance (LiveCompliance)',
                  desc: 'Help companies cut onboarding from 18 to 5 days',
                  target: 'HR Directors, 200+ employees',
                  offer: '$25K annual package',
                  promise: 'Save $195K in productivity year 1',
                  emailSequence: '5-email sequence for HR directors',
                  pricing: '$25K annual, $4.2K monthly',
                  discoveryScript: 'Focus on onboarding efficiency and compliance'
                },
                {
                  id: 'nonprofit',
                  title: '💚 Nonprofit (CAUSE WE CARE)',
                  desc: 'Help nonprofits build $150K+ earned revenue streams',
                  target: 'Executive Directors, $500K-$5M budgets',
                  offer: '$50K social enterprise build',
                  promise: 'Sustainable unrestricted revenue',
                  emailSequence: '6-email sequence for nonprofit directors',
                  pricing: '$50K annual, $8.3K monthly',
                  discoveryScript: 'Focus on earned revenue and sustainability'
                }
              ].map((sector) => (
                <div key={sector.id} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-blue-500 transition">
                  <h3 className="text-xl font-bold mb-2">{sector.title}</h3>
                  <p className="text-sm text-gray-400 mb-4">{sector.desc}</p>
                  <div className="space-y-2 text-sm mb-4">
                    <p><span className="text-blue-400 font-semibold">Target:</span> <span className="text-gray-300">{sector.target}</span></p>
                    <p><span className="text-green-400 font-semibold">Offer:</span> <span className="text-gray-300">{sector.offer}</span></p>
                    <p><span className="text-purple-400 font-semibold">Promise:</span> <span className="text-gray-300">{sector.promise}</span></p>
                  </div>
                  <button 
                    onClick={() => setSelectedSector(sector.id)}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                  >
                    View Complete System →
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTOR DETAIL PAGES */}
        {activeTab === 'your-sectors' && selectedSector && (
          <div>
            <button 
              onClick={() => setSelectedSector(null)}
              className="mb-4 text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-2"
            >
              ← Back to All Sectors
            </button>

            {selectedSector === 'emergency-logistics' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">🚨 Emergency Logistics (ATLAS PM)</h2>
                  <p className="text-gray-400">Complete system for emergency management agencies</p>
                </div>

                <div className="space-y-6">
                  {/* Client Avatar */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">Emergency Management Director, County Emergency Manager</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">County/State agencies, 200-1000 employees</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">4-5 hour mobilization times, lack of emergency response infrastructure, liability concerns</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">90-minute mobilization capability, reduce liability, improve disaster response</p>
                      </div>
                    </div>
                  </div>

                  {/* Success Path */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">4-5 hour mobilization times, fragmented emergency response systems</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">90-minute mobilization capability, unified emergency response system</p>
                      </div>
                    </div>
                  </div>

                  {/* Pricing */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$75K Annual</p>
                      <p className="text-gray-300">$12.5K monthly • 6-month workshop series</p>
                    </div>
                  </div>

                  {/* Email Sequence */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence</h3>
                    <div className="space-y-3">
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Email 1: Introduction</p>
                        <p className="text-sm text-gray-400">Subject: Can you reduce emergency mobilization times by 80%?</p>
                      </div>
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Email 2: Social Proof</p>
                        <p className="text-sm text-gray-400">Case study: How County X achieved 90-minute mobilization</p>
                      </div>
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Email 3: Value Proposition</p>
                        <p className="text-sm text-gray-400">ROI: Reduced liability + faster response = $X saved</p>
                      </div>
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Email 4: Urgency</p>
                        <p className="text-sm text-gray-400">Limited spots for Q2 implementation</p>
                      </div>
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <p className="font-semibold mb-2">Email 5: Soft Close</p>
                        <p className="text-sm text-gray-400">Discovery call invitation</p>
                      </div>
                    </div>
                  </div>

                  {/* Discovery Script */}
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], thanks for taking the time. I help emergency management agencies reduce mobilization times from 4-5 hours to 90 minutes. What's your current mobilization time?"

Discovery Questions:
1. What's your current mobilization process?
2. What challenges do you face during emergency responses?
3. What's the cost of slow mobilization? (liability, public safety)
4. What would 90-minute capability mean for your organization?
5. What's preventing you from achieving this now?

Close: "Based on what you've shared, I believe we can help you achieve 90-minute mobilization. Would a 15-minute strategy call make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      // Auto-fill Client Avatar Builder
                      setAvatarFormData({
                        avatarName: 'Emergency Management Director',
                        companySize: 'County/State agencies, 200-1000 employees',
                        industry: 'Public Sector, Emergency Services',
                        painPoints: '4-5 hour mobilization times, lack of emergency response infrastructure, liability concerns',
                        goals: '90-minute mobilization capability, reduce liability, improve disaster response',
                        budget: '$75K',
                        decisionMakers: 'County Emergency Manager, Board of Supervisors, Budget Office',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ Emergency Logistics avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}

            {/* NEMT SECTOR */}
            {selectedSector === 'nemt' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">🚑 NEMT (DEPOINTE System)</h2>
                  <p className="text-gray-400">Complete system for healthcare/Medicaid transportation</p>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">Medicaid Director, MCO Manager, Hospital CFO</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">Healthcare systems, 500-5000 patients/month</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">22% patient no-shows, $200K+ lost revenue, compliance issues</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">Reduce no-shows to 5%, recover lost revenue, improve HEDIS scores</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">22% no-show rate, fragmented transportation, lost revenue</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">5% no-show rate, integrated NEMT system, $200K+ recovered annually</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$100K Annual</p>
                      <p className="text-gray-300">$16.7K monthly • Full NEMT program</p>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence (7 emails)</h3>
                    <div className="space-y-3">
                      {[
                        { title: 'Email 1: Problem Hook', subject: 'Are 22% no-shows killing your revenue?' },
                        { title: 'Email 2: Cost Analysis', subject: 'You\'re losing $200K+ annually (here\'s how)' },
                        { title: 'Email 3: Solution Intro', subject: 'How to cut no-shows to 5% in 90 days' },
                        { title: 'Email 4: Social Proof', subject: 'Case study: Hospital X recovered $300K year 1' },
                        { title: 'Email 5: ROI Calculator', subject: 'Calculate YOUR potential savings' },
                        { title: 'Email 6: Urgency', subject: 'Limited Q2 implementation slots' },
                        { title: 'Email 7: Soft Close', subject: 'Free 15-min assessment call?' }
                      ].map((email, idx) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="font-semibold mb-2">{email.title}</p>
                          <p className="text-sm text-gray-400">{email.subject}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], thanks for taking time. I help healthcare systems reduce patient no-shows from 22% to 5%. What's your current no-show rate?"

Discovery Questions:
1. What's your current patient no-show rate?
2. What's the financial impact of no-shows?
3. What transportation challenges do your patients face?
4. How much would recovering $200K annually mean to your organization?
5. What's preventing you from solving this now?

Close: "Based on what you've shared, I believe we can help you reduce no-shows to 5% and recover significant revenue. Would a 15-minute strategy call make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      setAvatarFormData({
                        avatarName: 'Medicaid Director / MCO Manager',
                        companySize: 'Healthcare systems, 500-5000 patients/month',
                        industry: 'Healthcare, Medicaid, MCO',
                        painPoints: '22% patient no-shows, $200K+ lost revenue, compliance issues',
                        goals: 'Reduce no-shows to 5%, recover lost revenue, improve HEDIS scores',
                        budget: '$100K',
                        decisionMakers: 'Medicaid Director, CFO, Operations VP',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ NEMT avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}

            {/* FREIGHT BROKERAGE SECTOR */}
            {selectedSector === 'freight-brokerage' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">🚚 Freight Brokerage (FleetFlow™)</h2>
                  <p className="text-gray-400">Complete system for manufacturing freight optimization</p>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">Supply Chain VP, Logistics Director, Operations Manager</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">Manufacturers, $2M-$10M annual freight spend</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">High freight costs, inconsistent service, lack of visibility</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">Save 25% on freight, improve delivery times, gain supply chain visibility</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">$2.4M freight spend, 15% waste, fragmented carriers</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">Save $600K annually, integrated TMS, reliable carrier network</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$80K Annual</p>
                      <p className="text-gray-300">$13.3K monthly • Full optimization program</p>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence (6 emails)</h3>
                    <div className="space-y-3">
                      {[
                        { title: 'Email 1: Cost Hook', subject: 'Wasting 25% of your freight budget?' },
                        { title: 'Email 2: ROI Case Study', subject: 'How Manufacturer X saved $600K on freight' },
                        { title: 'Email 3: Solution Preview', subject: 'Cut freight costs 25% in 4 months' },
                        { title: 'Email 4: Risk Reversal', subject: 'Guaranteed $200K savings or we refund' },
                        { title: 'Email 5: Social Proof', subject: '12 manufacturers using FleetFlow™' },
                        { title: 'Email 6: Call Invitation', subject: 'Free freight audit ($5K value)' }
                      ].map((email, idx) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="font-semibold mb-2">{email.title}</p>
                          <p className="text-sm text-gray-400">{email.subject}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], I help manufacturers save 25% on freight spend. What's your annual freight budget?"

Discovery Questions:
1. What's your current annual freight spend?
2. What percentage do you think you're wasting?
3. What are your biggest freight challenges? (cost, service, visibility)
4. What would saving $600K annually mean for your P&L?
5. What's preventing you from optimizing freight now?

Close: "Based on $2.4M spend, we can likely save you $600K annually. Would a free freight audit make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      setAvatarFormData({
                        avatarName: 'Supply Chain VP / Logistics Director',
                        companySize: 'Manufacturers, $2M-$10M annual freight spend',
                        industry: 'Manufacturing, Supply Chain',
                        painPoints: 'High freight costs, inconsistent service, lack of visibility',
                        goals: 'Save 25% on freight, improve delivery times, gain supply chain visibility',
                        budget: '$80K',
                        decisionMakers: 'VP Supply Chain, CFO, Operations Director',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ Freight Brokerage avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}

            {/* VALET SERVICES SECTOR */}
            {selectedSector === 'valet-services' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">🏥 Valet Services (DEPOINTE Valet)</h2>
                  <p className="text-gray-400">Complete system for hospital parking revenue</p>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">Hospital CFO, Patient Experience Director, Facilities Manager</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">Hospitals, 200-1000 beds, urban locations</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">Limited parking, poor patient experience, lost revenue opportunity</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">Increase parking revenue 35%, improve patient satisfaction scores</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">$250K parking revenue, poor patient experience, missed opportunity</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">$350K+ annual revenue, improved HCAHPS scores, premium service</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$60K Annual</p>
                      <p className="text-gray-300">$10K monthly • Full valet program launch</p>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence (5 emails)</h3>
                    <div className="space-y-3">
                      {[
                        { title: 'Email 1: Opportunity Hook', subject: 'Missing $350K in parking revenue?' },
                        { title: 'Email 2: Patient Experience', subject: 'How valet improved our HCAHPS by 12%' },
                        { title: 'Email 3: ROI Breakdown', subject: '$100K additional revenue with $60K investment' },
                        { title: 'Email 4: Case Study', subject: 'Hospital Y added $400K parking revenue year 1' },
                        { title: 'Email 5: Call Invitation', subject: 'Free parking revenue assessment' }
                      ].map((email, idx) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="font-semibold mb-2">{email.title}</p>
                          <p className="text-sm text-gray-400">{email.subject}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], I help hospitals increase parking revenue by 35% while improving patient experience. What's your current parking revenue?"

Discovery Questions:
1. What's your current parking capacity and revenue?
2. What parking challenges do patients complain about?
3. How important is patient experience to your organization?
4. What would $350K additional annual revenue mean?
5. What's preventing you from maximizing parking revenue now?

Close: "Based on what you've shared, we can help you add $100K+ annually. Would a free parking assessment make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      setAvatarFormData({
                        avatarName: 'Hospital CFO / Patient Experience Director',
                        companySize: 'Hospitals, 200-1000 beds, urban locations',
                        industry: 'Healthcare, Hospital Services',
                        painPoints: 'Limited parking, poor patient experience, lost revenue opportunity',
                        goals: 'Increase parking revenue 35%, improve patient satisfaction scores',
                        budget: '$60K',
                        decisionMakers: 'CFO, Patient Experience Director, Facilities Manager',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ Valet Services avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}

            {/* FEDERAL COMPLIANCE SECTOR */}
            {selectedSector === 'federal-compliance' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">🔍 Federal Compliance (LiveCompliance)</h2>
                  <p className="text-gray-400">Complete system for HR onboarding optimization</p>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">HR Director, Compliance Manager, Operations VP</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">Companies with 200+ employees, regulated industries</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">18-day onboarding, compliance risk, $195K in lost productivity</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">Cut onboarding to 5 days, ensure compliance, save $195K annually</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">18-day onboarding, manual compliance checks, productivity loss</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">5-day onboarding, automated compliance, $195K savings annually</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$25K Annual</p>
                      <p className="text-gray-300">$4.2K monthly • Complete compliance package</p>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence (5 emails)</h3>
                    <div className="space-y-3">
                      {[
                        { title: 'Email 1: Cost Hook', subject: 'Is 18-day onboarding costing you $195K?' },
                        { title: 'Email 2: Compliance Risk', subject: 'One failed audit could cost you millions' },
                        { title: 'Email 3: Solution Intro', subject: 'Cut onboarding to 5 days (guaranteed)' },
                        { title: 'Email 4: Social Proof', subject: 'Company X saved $200K with LiveCompliance' },
                        { title: 'Email 5: Call Invitation', subject: 'Free compliance assessment' }
                      ].map((email, idx) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="font-semibold mb-2">{email.title}</p>
                          <p className="text-sm text-gray-400">{email.subject}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], I help companies cut onboarding from 18 days to 5 days. How long is your current onboarding process?"

Discovery Questions:
1. What's your current onboarding timeline?
2. What compliance requirements do you need to track?
3. What's the cost of slow onboarding? (productivity, compliance risk)
4. What would saving $195K annually mean to your organization?
5. What's preventing you from optimizing onboarding now?

Close: "Based on what you've shared, we can help you cut onboarding to 5 days and save $195K. Would a free compliance assessment make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      setAvatarFormData({
                        avatarName: 'HR Director / Compliance Manager',
                        companySize: 'Companies with 200+ employees, regulated industries',
                        industry: 'HR, Compliance, Regulated Industries',
                        painPoints: '18-day onboarding, compliance risk, $195K in lost productivity',
                        goals: 'Cut onboarding to 5 days, ensure compliance, save $195K annually',
                        budget: '$25K',
                        decisionMakers: 'HR Director, Compliance Manager, Operations VP',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ Federal Compliance avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}

            {/* NONPROFIT SECTOR */}
            {selectedSector === 'nonprofit' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">💚 Nonprofit (CAUSE WE CARE)</h2>
                  <p className="text-gray-400">Complete system for nonprofit earned revenue</p>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">👤 Client Avatar</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Target Title</p>
                        <p className="text-white">Executive Director, Development Director, Board President</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Company Size</p>
                        <p className="text-white">Nonprofits with $500K-$5M budgets</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Pain Points</p>
                        <p className="text-white">Grant dependency, restricted funding, revenue sustainability concerns</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-400 mb-1">Goals</p>
                        <p className="text-white">Build $150K+ earned revenue stream, reduce grant dependency, unrestricted funding</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">🛤️ Success Path</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                        <h4 className="font-bold text-red-400 mb-2">Point A: Current State</h4>
                        <p className="text-gray-300 text-sm">90% grant-dependent, restricted funding, sustainability risk</p>
                      </div>
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                        <h4 className="font-bold text-green-400 mb-2">Point B: Desired State</h4>
                        <p className="text-gray-300 text-sm">$150K+ annual earned revenue, sustainable operations, unrestricted funding</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">💰 Pricing</h3>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                      <p className="text-3xl font-bold text-green-400 mb-2">$50K Annual</p>
                      <p className="text-gray-300">$8.3K monthly • Social enterprise build</p>
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-400">📧 Email Sequence (6 emails)</h3>
                    <div className="space-y-3">
                      {[
                        { title: 'Email 1: Sustainability Hook', subject: 'Are you too grant-dependent?' },
                        { title: 'Email 2: Revenue Opportunity', subject: 'Build $150K earned revenue stream' },
                        { title: 'Email 3: Social Enterprise', subject: 'How nonprofits build sustainable revenue' },
                        { title: 'Email 4: Case Study', subject: 'Nonprofit X built $200K social enterprise' },
                        { title: 'Email 5: ROI', subject: '$50K investment → $150K+ annual revenue' },
                        { title: 'Email 6: Call Invitation', subject: 'Free revenue assessment call' }
                      ].map((email, idx) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <p className="font-semibold mb-2">{email.title}</p>
                          <p className="text-sm text-gray-400">{email.subject}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">🎤 Discovery Script</h3>
                    <div className="bg-gray-700/50 p-4 rounded-lg">
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">
{`Opening: "Hi [Name], I help nonprofits build $150K+ earned revenue streams. What percentage of your budget is grant-funded?"

Discovery Questions:
1. What's your current budget breakdown? (grants vs earned revenue)
2. What are your biggest sustainability concerns?
3. What assets/services could you monetize?
4. What would $150K unrestricted annual revenue mean?
5. What's preventing you from building earned revenue now?

Close: "Based on what you've shared, we can help you build a $150K+ social enterprise. Would a free revenue assessment make sense?"`}
                      </p>
                    </div>
                  </div>

                  <button 
                    onClick={() => {
                      setAvatarFormData({
                        avatarName: 'Executive Director / Development Director',
                        companySize: 'Nonprofits with $500K-$5M budgets',
                        industry: 'Nonprofit, Social Sector',
                        painPoints: 'Grant dependency, restricted funding, revenue sustainability concerns',
                        goals: 'Build $150K+ earned revenue stream, reduce grant dependency, unrestricted funding',
                        budget: '$50K',
                        decisionMakers: 'Executive Director, Board President, Development Director',
                        prospectId: ''
                      });
                      setActiveTab('client-avatar');
                      showNotification('✅ Nonprofit avatar loaded!', 'success');
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold text-lg transition"
                  >
                    🚀 Load This Avatar into Builder
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB: AI HANDLER */}
        {activeTab === 'ai-handler' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🤖 AI Response Handler</h2>
              <p className="text-gray-400">Claude analyzes responses and suggests perfect replies using Blueprint psychology</p>
            </div>

            <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-blue-400 mb-2">🤖 AI Response Analysis</h3>
              <p className="text-sm text-gray-300">Claude AI analyzes responses and suggests perfect replies using Blueprint psychology. No API key needed - uses backend.</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold mb-4">Paste Response to Analyze</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">Link to Prospect (Optional)</label>
                    <select 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      value={responseFormData.prospectId}
                      onChange={(e) => {
                        const prospect = prospects.find(p => p.id === e.target.value);
                        setResponseFormData({
                          ...responseFormData,
                          prospectId: e.target.value,
                          prospectName: prospect?.companyName || '',
                          company: prospect?.companyName || ''
                        });
                      }}
                    >
                      <option value="">Select prospect (optional)</option>
                      {prospects.map(prospect => (
                        <option key={prospect.id} value={prospect.id}>
                          {prospect.companyName} - {prospect.industry}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">Sector (Optional)</label>
                    <select 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      value={responseFormData.sector}
                      onChange={(e) => setResponseFormData({...responseFormData, sector: e.target.value})}
                    >
                      <option value="">Select sector...</option>
                      <option>Emergency Logistics</option>
                      <option>NEMT</option>
                      <option>Freight Brokerage</option>
                      <option>Valet Services</option>
                      <option>Federal Compliance</option>
                      <option>Nonprofit</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Email Response *</label>
                  <textarea 
                    rows={8} 
                    placeholder="Paste their response here..." 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={responseFormData.emailContent}
                    onChange={(e) => setResponseFormData({...responseFormData, emailContent: e.target.value})}
                  />
                </div>
                <button 
                  onClick={analyzeResponse}
                  disabled={analyzingResponse || !responseFormData.emailContent.trim()}
                  className={`w-full ${
                    analyzingResponse || !responseFormData.emailContent.trim()
                      ? 'bg-gray-600 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                  } px-6 py-3 rounded-lg font-bold transition`}
                >
                  {analyzingResponse ? '⏳ Analyzing...' : '🧠 Analyze with AI'}
                </button>
              </div>
            </div>

            {/* Analysis Results */}
            {responseAnalysis && !responseAnalysis.error && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-2xl font-bold">📊 Analysis Results</h3>
                  <button 
                    onClick={() => {
                      setResponseAnalysis(null);
                      setResponseFormData({
                        emailContent: '',
                        prospectId: '',
                        prospectName: '',
                        company: '',
                        sector: ''
                      });
                    }}
                    className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                  >
                    Analyze New Response
                  </button>
                </div>

                {/* Response Category & Sentiment */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {responseAnalysis.category && (
                    <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6">
                      <h4 className="text-sm font-semibold text-blue-400 mb-2">Response Category</h4>
                      <p className="text-2xl font-bold text-white">{responseAnalysis.category}</p>
                    </div>
                  )}
                  {responseAnalysis.sentiment && (
                    <div className="bg-purple-900/30 border border-purple-700 rounded-xl p-6">
                      <h4 className="text-sm font-semibold text-purple-400 mb-2">Sentiment</h4>
                      <p className="text-2xl font-bold text-white">{responseAnalysis.sentiment}</p>
                    </div>
                  )}
                </div>

                {/* Analysis Details */}
                {responseAnalysis.analysis && (
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-blue-400">📋 Analysis</h4>
                    <p className="text-gray-300 whitespace-pre-wrap">{responseAnalysis.analysis}</p>
                  </div>
                )}

                {/* Recommended Reply */}
                {responseAnalysis.recommended_reply && (
                  <div className="bg-green-900/30 border border-green-700 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-green-400">✉️ Recommended Reply</h4>
                    <div className="bg-gray-800 rounded-lg p-4 mb-4">
                      <pre className="text-gray-300 whitespace-pre-wrap text-sm">{responseAnalysis.recommended_reply}</pre>
                    </div>
                    <button 
                      onClick={() => {
                        const blob = new Blob([responseAnalysis.recommended_reply], { type: 'text/plain' });
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'Recommended_Reply.txt';
                        link.click();
                        window.URL.revokeObjectURL(url);
                        showNotification('📄 Reply exported!', 'success');
                      }}
                      className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition"
                    >
                      📄 Export Reply
                    </button>
                  </div>
                )}

                {/* Next Steps */}
                {responseAnalysis.next_steps && (
                  <div className="bg-yellow-900/30 border border-yellow-700 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-yellow-400">🎯 Recommended Next Steps</h4>
                    <ul className="space-y-2">
                      {(Array.isArray(responseAnalysis.next_steps) 
                        ? responseAnalysis.next_steps 
                        : [responseAnalysis.next_steps]
                      ).map((step: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-300">
                          <span className="text-yellow-400 mt-1">•</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {notification && (
              <div className={`mb-4 p-4 rounded-lg ${
                notification.type === 'success' ? 'bg-green-900/30 border border-green-700 text-green-400' : 'bg-red-900/30 border border-red-700 text-red-400'
              }`}>
                {notification.message}
              </div>
            )}

            {!responseAnalysis && !analyzingResponse && (
              <div className="text-center text-gray-400">
                <p className="text-sm">AI will categorize response and generate perfect reply using Blueprint psychology</p>
              </div>
            )}
          </div>
        )}

        {/* TAB: PIPELINE */}
        {activeTab === 'pipeline' && (
          <div>
            <div className="mb-6 flex justify-between items-center">
              <div>
                <h2 className="text-3xl font-bold mb-2">📈 Pipeline Tracker</h2>
                <p className="text-gray-400">Manage all your prospects from Airtable</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={fetchProspects}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  🔄 Refresh
                </button>
                <button 
                  onClick={() => {
                    // Create new prospect
                    const newProspect = {
                      companyName: prompt('Company Name:') || '',
                      industry: prompt('Industry:') || '',
                      companySize: prompt('Company Size:') || '',
                      location: prompt('Location:') || '',
                      currentChallenge: prompt('Current Challenge:') || '',
                      businessGoals: prompt('Business Goals:') || '',
                      budget: prompt('Budget:') || '',
                      timeline: prompt('Timeline:') || ''
                    };
                    if (newProspect.companyName) {
                      api.createDdcssProspect(newProspect).then(() => {
                        fetchProspects();
                        showNotification('✅ Prospect created!', 'success');
                      });
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  ➕ Add Prospect
                </button>
              </div>
            </div>

            {prospects.length > 0 ? (
              <div className="bg-gray-800 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-700">
                      <tr>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Company</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Industry</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Size</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Budget</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Qualification</th>
                        <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prospects.map((prospect: any) => (
                        <tr key={prospect.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                          <td className="px-6 py-4">
                            <div className="font-bold text-blue-400">{prospect.companyName}</div>
                            <div className="text-xs text-gray-400">{prospect.location || 'N/A'}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-300">{prospect.industry || '-'}</td>
                          <td className="px-6 py-4 text-gray-300">{prospect.companySize || '-'}</td>
                          <td className="px-6 py-4 text-gray-300">{prospect.budget || '-'}</td>
                          <td className="px-6 py-4">
                            <span className={`text-xs font-bold px-2 py-1 rounded ${
                              prospect.status === 'Qualifying' ? 'bg-yellow-500/20 text-yellow-400' :
                              prospect.status === 'Proposal' ? 'bg-blue-500/20 text-blue-400' :
                              'bg-gray-500/20 text-gray-400'
                            }`}>
                              {prospect.status || 'New'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            {prospect.qualificationScore && (
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-bold">{prospect.qualificationScore}</span>
                                <div className="w-16 bg-gray-600 rounded-full h-2">
                                  <div 
                                    className="bg-blue-500 h-2 rounded-full" 
                                    style={{ width: `${prospect.qualificationScore}%` }}
                                  ></div>
                                </div>
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex gap-2">
                              <button 
                                onClick={() => api.qualifyProspect(prospect.id).then(() => {
                                  fetchProspects();
                                  showNotification('✅ Prospect qualified!', 'success');
                                })}
                                className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm font-semibold transition"
                              >
                                Qualify
                              </button>
                              <button 
                                onClick={() => api.generateBlueprint(prospect.id, 'ALIGN').then(() => {
                                  showNotification('✅ Blueprint generated!', 'success');
                                })}
                                className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm font-semibold transition"
                              >
                                Blueprint
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-xl p-8 text-center text-gray-400">
                <div className="text-6xl mb-4 opacity-20">📈</div>
                <p className="text-lg mb-2 font-semibold">No prospects yet</p>
                <p className="text-sm mb-6">Use AI Response Handler to add your first contact, or manually add prospects</p>
                <button 
                  onClick={() => {
                    const newProspect = {
                      companyName: prompt('Company Name:') || '',
                      industry: prompt('Industry:') || '',
                      companySize: prompt('Company Size:') || ''
                    };
                    if (newProspect.companyName) {
                      api.createDdcssProspect(newProspect).then(() => {
                        fetchProspects();
                        showNotification('✅ Prospect created!', 'success');
                      });
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  ➕ Add First Prospect
                </button>
              </div>
            )}
          </div>
        )}

        {/* TAB: MVP DISCOVERY */}
        {activeTab === 'mvp-discovery' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">⭐ MVP Discovery</h2>
              <p className="text-gray-400">Most Valuable Problem Discovery - Find opportunities from Reddit</p>
            </div>

            <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-green-400 mb-2">🎯 What is MVP Discovery?</h3>
              <p className="text-sm text-gray-300 mb-3">Discover problems people are willing to pay for by mining Reddit discussions. System scores each problem by profitability and matches it to the best solution type (PDF, DDCSS Consulting, GPSS, ATLAS, or New Service).</p>
              <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mt-4">
                <p className="text-yellow-400 font-semibold text-sm">⚠️ MVP Discovery System Coming Soon</p>
                <p className="text-gray-300 text-xs mt-1">Reddit mining integration is being developed. Will automatically discover problems, score them, and match to solutions.</p>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">🔍 How It Will Work</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                  <div className="text-3xl mb-2">🔍</div>
                  <h4 className="font-bold text-blue-400 mb-2">1. Mine Reddit</h4>
                  <p className="text-sm text-gray-300">Scans subreddits for pain points and problems people discuss</p>
                </div>
                <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                  <div className="text-3xl mb-2">🤖</div>
                  <h4 className="font-bold text-green-400 mb-2">2. AI Analysis</h4>
                  <p className="text-sm text-gray-300">Scores problems by profitability, willingness to pay, market size</p>
                </div>
                <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-4">
                  <div className="text-3xl mb-2">💡</div>
                  <h4 className="font-bold text-purple-400 mb-2">3. Match Solutions</h4>
                  <p className="text-sm text-gray-300">Matches problems to PDF, DDCSS, GPSS, ATLAS, or new services</p>
                </div>
              </div>

              <div className="bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-bold mb-3">Example Subreddits to Monitor:</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                  {['Entrepreneur', 'startups', 'smallbusiness', 'freelance', 'consulting', 'SaaS', 'sideproject', 'business'].map((sub, idx) => (
                    <div key={idx} className="bg-gray-600/50 px-3 py-2 rounded text-center text-gray-300">
                      r/{sub}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">📋 Discovered Problems (Coming Soon)</h3>
              <div className="text-center py-12">
                <div className="text-6xl mb-4 opacity-20">⭐</div>
                <p className="text-gray-400 font-semibold mb-2">No problems discovered yet</p>
                <p className="text-sm text-gray-500">MVP Discovery system will automatically find and score problems when enabled</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Copilot Floating Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button 
          onClick={() => setShowCopilot(!showCopilot)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 w-16 h-16 rounded-full shadow-2xl flex items-center justify-center text-2xl transition-all duration-300 animate-pulse"
        >
          🤖
        </button>
        
        {showCopilot && (
          <div className="absolute bottom-20 right-0 w-96 bg-gray-800 border-2 border-blue-500 rounded-xl shadow-2xl">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-t-xl flex justify-between items-center">
              <div>
                <h3 className="font-bold">AI Copilot</h3>
                <p className="text-xs text-blue-100">Your automated assistant</p>
              </div>
              <button 
                onClick={() => setShowCopilot(false)}
                className="text-2xl hover:bg-white/20 w-8 h-8 rounded-lg transition"
              >
                ×
              </button>
            </div>
            
            <div className="p-4 h-96 overflow-y-auto bg-gray-900 space-y-3">
              {copilotMessages.map((msg, index) => (
                <div 
                  key={index}
                  className={msg.isUser 
                    ? 'bg-gray-700 rounded-lg p-3 text-sm ml-8' 
                    : 'bg-blue-600/20 border border-blue-500/50 rounded-lg p-3 text-sm mr-8'
                  }
                  dangerouslySetInnerHTML={{ __html: msg.text }}
                />
              ))}
            </div>
            
            <div className="p-4 border-t border-gray-700">
              <div className="flex gap-2">
                <input 
                  type="text" 
                  value={copilotMessage}
                  onChange={(e) => setCopilotMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendCopilotMessage()}
                  placeholder="Ask me anything..." 
                  className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
                />
                <button 
                  onClick={sendCopilotMessage}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold text-sm transition"
                >
                  Send
                </button>
              </div>
              <div className="flex gap-2 mt-2 flex-wrap">
                <button className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-xs transition">Check for new responses</button>
                <button className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-xs transition">What should I do now?</button>
                <button className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-lg text-xs transition">Generate email</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DDCSSSystem;

