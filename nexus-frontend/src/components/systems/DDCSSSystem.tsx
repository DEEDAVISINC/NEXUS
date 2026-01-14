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

  // Client Avatar Functions
  const createClientAvatar = async () => {
    try {
      const response = await api.createDdcssClientAvatar(avatarFormData);
      if (response.avatar) {
        showNotification('✅ Client Avatar created with AI analysis!', 'success');
        setAvatarAnalysis(response.aiAnalysis || null);
        setAvatarFormData({
          avatarName: '',
          companySize: '',
          industry: '',
          painPoints: '',
          goals: '',
          budget: '',
          decisionMakers: '',
          prospectId: ''
        });
      }
    } catch (error) {
      showNotification('❌ Error creating client avatar', 'error');
    }
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

  // Dashboard Stats (will be calculated from prospects)
  const [dashboardStats, setDashboardStats] = useState({
    activePipeline: 0,
    thisMonth: 0,
    callsBooked: 0,
    pipelineValue: 0
  });

  // Update dashboard stats when prospects change
  useEffect(() => {
    if (prospects.length > 0) {
      const activeProspects = prospects.filter((p: any) => 
        p.status === 'New' || p.status === 'Qualifying' || p.status === 'Proposal'
      );
      const totalValue = activeProspects.reduce((sum: number, p: any) => {
        const budget = p.budget || '';
        // Extract number from budget string like "$25K-$50K"
        const match = budget.match(/\$?(\d+)K/i);
        if (match) {
          return sum + (parseInt(match[1]) * 1000);
        }
        return sum;
      }, 0);

      setDashboardStats({
        activePipeline: activeProspects.length,
        thisMonth: 0, // Would need date tracking for this
        callsBooked: 0, // Would need call tracking
        pipelineValue: totalValue
      });
    }
  }, [prospects]);

  const stats = [
    { label: 'Active Pipeline', value: dashboardStats.activePipeline.toString(), subtext: 'Prospects', gradient: 'from-blue-600 to-blue-800' },
    { label: 'This Month', value: dashboardStats.thisMonth.toString(), subtext: 'Responses', gradient: 'from-green-600 to-green-800' },
    { label: 'Calls Booked', value: dashboardStats.callsBooked.toString(), subtext: 'This Quarter', gradient: 'from-purple-600 to-purple-800' },
    { label: 'Pipeline Value', value: `$${(dashboardStats.pipelineValue / 1000).toFixed(0)}K`, subtext: 'Total', gradient: 'from-yellow-600 to-yellow-800' }
  ];

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
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">Welcome to DDCSS v2.0</h2>
              <p className="text-gray-400">Your complete consulting sales system with Blueprint framework integrated</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              {stats.map((stat, index) => (
                <div key={index} className={`bg-gradient-to-br ${stat.gradient} p-6 rounded-xl`}>
                  <h3 className="text-sm font-semibold text-white/80 mb-2">{stat.label}</h3>
                  <p className="text-4xl font-bold mb-1">{stat.value}</p>
                  <p className="text-sm text-white/70">{stat.subtext}</p>
                </div>
              ))}
            </div>

            {/* Recent Prospects */}
            {prospects.length > 0 && (
              <div className="bg-gray-800 rounded-xl p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">Recent Prospects</h3>
                  <button 
                    onClick={() => setActiveTab('pipeline')}
                    className="text-blue-400 hover:text-blue-300 font-semibold"
                  >
                    View All →
                  </button>
                </div>
                <div className="space-y-3">
                  {prospects.slice(0, 5).map((prospect: any) => (
                    <div key={prospect.id} className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <h4 className="font-bold text-blue-400">{prospect.companyName}</h4>
                          <p className="text-sm text-gray-400">{prospect.industry} • {prospect.companySize}</p>
                        </div>
                        <span className={`text-xs font-bold px-2 py-1 rounded ${
                          prospect.status === 'Qualifying' ? 'bg-yellow-500/20 text-yellow-400' :
                          prospect.status === 'Proposal' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {prospect.status || 'New'}
                        </span>
                      </div>
                      {prospect.budget && (
                        <div className="text-sm text-gray-300">
                          Budget: <span className="text-green-400 font-semibold">{prospect.budget}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Blueprint Progress */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Your Blueprint Progress</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                  { name: 'ALIGN', desc: 'Define purpose', tab: 'blueprint' },
                  { name: 'DEFINE', desc: 'Who you serve', tab: 'client-avatar' },
                  { name: 'DESIGN', desc: 'Build offer', tab: 'success-path' },
                  { name: 'SHINE', desc: 'Craft message', tab: 'pitchmap' }
                ].map((framework, index) => (
                  <div 
                    key={framework.name} 
                    className="text-center cursor-pointer hover:scale-105 transition"
                    onClick={() => setActiveTab(framework.tab)}
                  >
                    <div className="w-16 h-16 mx-auto mb-3 border-4 border-gray-600 rounded-full flex items-center justify-center">
                      <span className="text-2xl font-bold">0%</span>
                    </div>
                    <p className="font-semibold">{framework.name}</p>
                    <p className="text-xs text-gray-400">{framework.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Automated Workflows & AI Copilot */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">🤖 Automated Workflows (Active)</h3>
                <div className="space-y-3">
                  <div className="bg-green-900/30 border border-green-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <p className="font-semibold">Email Monitoring</p>
                      </div>
                      <span className="text-xs bg-green-500/20 px-2 py-1 rounded text-green-400">RUNNING</span>
                    </div>
                    <p className="text-xs text-gray-400">Auto-checks Gmail every hour for responses</p>
                    <p className="text-xs text-green-400 mt-1">Last check: 2 min ago • Next: 58 min</p>
                  </div>
                  
                  <div className="bg-green-900/30 border border-green-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <p className="font-semibold">AI Response Analysis</p>
                      </div>
                      <span className="text-xs bg-green-500/20 px-2 py-1 rounded text-green-400">RUNNING</span>
                    </div>
                    <p className="text-xs text-gray-400">Auto-analyzes responses, suggests replies</p>
                    <p className="text-xs text-green-400 mt-1">0 responses waiting for review</p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">⚡ AI Copilot Suggestions</h3>
                <div className="space-y-3">
                  <div className="bg-blue-900/30 border border-blue-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">💡</span>
                      <p className="font-semibold text-blue-400">Ready to Start?</p>
                    </div>
                    <p className="text-sm text-gray-300 mb-3">I recommend starting with your pre-built Emergency Logistics sector. It's ready to go!</p>
                    <button 
                      onClick={() => setActiveTab('your-sectors')}
                      className="w-full bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg text-sm font-semibold transition"
                    >
                      View Your 6 Sectors →
                    </button>
                  </div>

                  <div className="bg-purple-900/30 border border-purple-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">📧</span>
                      <p className="font-semibold text-purple-400">No Contacts Yet</p>
                    </div>
                    <p className="text-sm text-gray-300 mb-3">Want me to help you build your first prospect list? I can generate 75 contacts in your target sector.</p>
                    <button className="w-full bg-purple-600 hover:bg-purple-700 px-3 py-2 rounded-lg text-sm font-semibold transition">
                      Build Prospect List →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* What Happens Automatically */}
            <div className="mt-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4 text-center">🔄 What Happens Automatically (You Just Approve)</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { icon: '📨', title: 'Email Monitoring', desc: 'Checks Gmail hourly, extracts responses' },
                  { icon: '🤖', title: 'AI Analysis', desc: 'Categorizes, suggests perfect reply' },
                  { icon: '📊', title: 'Pipeline Update', desc: 'Moves prospects, flags urgent' },
                  { icon: '✅', title: 'You Approve', desc: 'Review, personalize, send (2 min)' }
                ].map((item) => (
                  <div key={item.title} className="text-center">
                    <div className="text-4xl mb-2">{item.icon}</div>
                    <p className="font-semibold text-sm mb-1">{item.title}</p>
                    <p className="text-xs text-gray-400">{item.desc}</p>
                  </div>
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
                    <h3 className="text-2xl font-bold mb-3">DEFINE - Clarify Who You Serve & Results You Deliver</h3>
                    <p className="text-green-100 mb-4">"Specialists stand out, attract premium clients, and command higher fees"</p>
                    
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
                    <h3 className="text-2xl font-bold mb-3">DESIGN - Turn Expertise Into High-Value Offer</h3>
                    <p className="text-purple-100 mb-4">"Strong offer = clear promise of transformation + proven process + confidence positioning"</p>
                    
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
                    <h3 className="text-2xl font-bold mb-3">SHINE - Attract Ideal Clients With Memorable Message</h3>
                    <p className="text-yellow-100 mb-4">"Your offer might be powerful, but if you can't communicate it clearly—your ideal clients won't buy it"</p>
                    
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
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">👤 Client Avatar Builder</h2>
              <p className="text-gray-400">Define your ideal client with precision - "Find the smallest nesting doll"</p>
            </div>

            <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-blue-400 mb-2">💡 Why This Matters</h3>
              <p className="text-sm text-gray-300">"The more precisely you define your ideal client, the more effectively you can speak to their needs. Specialists command premium fees because they understand their niche deeply."</p>
            </div>

            {/* Prospect Selection */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Link to Prospect (Optional)</h3>
              <select 
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                value={avatarFormData.prospectId}
                onChange={(e) => setAvatarFormData({...avatarFormData, prospectId: e.target.value})}
              >
                <option value="">Create new avatar (not linked)</option>
                {prospects.map(prospect => (
                  <option key={prospect.id} value={prospect.id}>
                    {prospect.companyName} - {prospect.industry}
                  </option>
                ))}
              </select>
            </div>

            {/* Layer 1: Professional Profile */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Layer 1: Professional Profile</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Avatar Name *</label>
                  <input 
                    type="text" 
                    placeholder="e.g., Emergency Management Director" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.avatarName}
                    onChange={(e) => setAvatarFormData({...avatarFormData, avatarName: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Company Size *</label>
                  <input 
                    type="text" 
                    placeholder="e.g., 200-1000 employees" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.companySize}
                    onChange={(e) => setAvatarFormData({...avatarFormData, companySize: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Industry/Sector *</label>
                  <input 
                    type="text" 
                    placeholder="e.g., Public Sector, Emergency Services" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.industry}
                    onChange={(e) => setAvatarFormData({...avatarFormData, industry: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Budget Range</label>
                  <input 
                    type="text" 
                    placeholder="e.g., $25K-$100K" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.budget}
                    onChange={(e) => setAvatarFormData({...avatarFormData, budget: e.target.value})}
                  />
                </div>
              </div>
            </div>

            {/* Layer 2: Personal Motivators */}
            <div className="bg-gray-800 rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Layer 2: Personal Motivators</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Pain Points *</label>
                  <textarea 
                    rows={3} 
                    placeholder="e.g., 4-5 hour mobilization times, lack of emergency response infrastructure, liability concerns" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.painPoints}
                    onChange={(e) => setAvatarFormData({...avatarFormData, painPoints: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Goals *</label>
                  <textarea 
                    rows={3} 
                    placeholder="e.g., Improve emergency response times, reduce liability, get promoted, reduce costs" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.goals}
                    onChange={(e) => setAvatarFormData({...avatarFormData, goals: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Decision Makers</label>
                  <textarea 
                    rows={2} 
                    placeholder="e.g., County Emergency Manager, Board of Supervisors, Budget Office" 
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    value={avatarFormData.decisionMakers}
                    onChange={(e) => setAvatarFormData({...avatarFormData, decisionMakers: e.target.value})}
                  />
                </div>
              </div>
            </div>

            {/* AI Analysis Results */}
            {avatarAnalysis && (
              <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6 mb-6">
                <h3 className="text-xl font-bold mb-4 text-blue-400">🤖 AI Analysis</h3>
                {avatarAnalysis.qualification_score && (
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-gray-300">Qualification Score:</span>
                      <span className="text-2xl font-bold text-blue-400">{avatarAnalysis.qualification_score}/100</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${avatarAnalysis.qualification_score}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                {avatarAnalysis.recommended_approach && (
                  <div className="text-gray-300 mb-2">
                    <strong>Recommended Approach:</strong> {avatarAnalysis.recommended_approach}
                  </div>
                )}
                {avatarAnalysis.win_probability && (
                  <div className="text-gray-300">
                    <strong>Win Probability:</strong> {avatarAnalysis.win_probability}%
                  </div>
                )}
              </div>
            )}

            {/* Notification */}
            {notification && (
              <div className={`mb-4 p-4 rounded-lg ${
                notification.type === 'success' ? 'bg-green-900/30 border border-green-700 text-green-400' : 'bg-red-900/30 border border-red-700 text-red-400'
              }`}>
                {notification.message}
              </div>
            )}

            <div className="flex gap-3">
              <button 
                onClick={createClientAvatar}
                className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
              >
                💾 Save Avatar & Analyze with AI
              </button>
              <button onClick={() => setActiveTab('success-path')} className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg font-semibold transition">
                Next: Build Success Path →
              </button>
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

            {/* Other sectors would follow same pattern - truncated for brevity */}
            {selectedSector && selectedSector !== 'emergency-logistics' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-3xl font-bold mb-2">
                    {selectedSector === 'nemt' && '🚑 NEMT (DEPOINTE System)'}
                    {selectedSector === 'freight-brokerage' && '🚚 Freight Brokerage (FleetFlow™)'}
                    {selectedSector === 'valet-services' && '🏥 Valet Services (DEPOINTE Valet)'}
                    {selectedSector === 'federal-compliance' && '🔍 Federal Compliance (LiveCompliance)'}
                    {selectedSector === 'nonprofit' && '💚 Nonprofit (CAUSE WE CARE)'}
                  </h2>
                  <p className="text-gray-400">Complete sector system</p>
                </div>
                <div className="bg-gray-800 rounded-xl p-8 text-center">
                  <p className="text-gray-400">Sector detail pages coming soon. Emergency Logistics sector is fully functional above!</p>
                  <button 
                    onClick={() => setSelectedSector('emergency-logistics')}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                  >
                    View Emergency Logistics →
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

