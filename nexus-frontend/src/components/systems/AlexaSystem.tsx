import React, { useState, useEffect } from 'react';

interface AlexaSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface HealthStatus {
  status: string;
  service: string;
  connected_to_nexus: string;
  intents_handled: number;
}

const VOICE_COMMANDS = [
  {
    category: 'Daily Operations',
    icon: '📋',
    commands: [
      { phrase: 'Give me my daily briefing', description: 'Priority actions and executive summary' },
      { phrase: "What's my priority today?", description: 'Top actions NEXUS recommends' },
      { phrase: "What's my daily target?", description: 'NOVA opportunity progress (3/day goal)' },
      { phrase: 'What bids are in progress?', description: 'Workflow checklist status across bids' },
      { phrase: 'Who needs a follow-up?', description: 'Buyer outreach tracking' },
      { phrase: "What's ready to send?", description: 'Check SEND_TO folders for complete packages' },
    ]
  },
  {
    category: 'Opportunity Discovery (NOVA)',
    icon: '🌟',
    commands: [
      { phrase: 'Find federal opportunities', description: 'Search SAM.gov for matching contracts' },
      { phrase: 'Find EDWOSB set-asides', description: 'Woman-owned small business set-asides' },
      { phrase: 'Find micro-purchases', description: 'Quick wins under $10K' },
      { phrase: 'Add to pipeline', description: 'Add opportunity to GPSS' },
      { phrase: 'Any new awards?', description: 'Win/loss tracking and success rate' },
    ]
  },
  {
    category: 'Pipeline (GPSS)',
    icon: '🎯',
    commands: [
      { phrase: 'Show me my pipeline', description: 'Open GPSS overview' },
      { phrase: 'How many opportunities do I have?', description: 'Pipeline stats and value' },
      { phrase: "What's my pipeline value?", description: 'Total dollar value in pipeline' },
      { phrase: 'Show me pipeline by agency', description: 'Pipeline filtered by agency' },
      { phrase: 'Which contracts should I pursue?', description: 'Bid opportunity prioritization' },
    ]
  },
  {
    category: 'Documents (PRISM)',
    icon: '📄',
    commands: [
      { phrase: 'Generate a capability statement for the VA', description: 'Cap statement with ProposalBio' },
      { phrase: 'Generate a quote response', description: 'Full multi-page bid response' },
      { phrase: 'Generate a compliance report', description: 'Status report generation' },
      { phrase: 'Generate my weekly executive report', description: 'Autonomous report generation' },
    ]
  },
  {
    category: 'Project Management (ATLAS)',
    icon: '📊',
    commands: [
      { phrase: 'Show me project health', description: 'Schedule, budget, quality, risk' },
      { phrase: 'Show me project milestones', description: 'Milestone tracking and deadlines' },
      { phrase: 'What tasks need completion?', description: 'Overdue and pending tasks' },
      { phrase: 'Show me team capacity', description: 'Workload and availability' },
      { phrase: 'Show me project risks', description: 'Risk register and mitigation plans' },
    ]
  },
  {
    category: 'Compliance & Contracts',
    icon: '✅',
    commands: [
      { phrase: "What's my compliance status?", description: 'Certification and regulatory tracking' },
      { phrase: 'What subs need onboarding?', description: '6-pillar subcontractor framework' },
      { phrase: 'Show me contract deadlines', description: 'Upcoming deliverables and milestones' },
      { phrase: "What's my win probability?", description: 'Competitive analysis on bids' },
      { phrase: 'Show me contract performance', description: 'CPARS, on-time delivery, quality' },
    ]
  },
  {
    category: 'Financial (VERTEX)',
    icon: '💰',
    commands: [
      { phrase: 'Show me revenue by division', description: 'Financial metrics breakdown' },
      { phrase: 'What invoices are past due?', description: 'Invoice and AR tracking' },
      { phrase: 'Show me project budget', description: 'Budget allocation and variance' },
      { phrase: 'Log an expense', description: 'Expense tracking' },
    ]
  },
  {
    category: 'AI Intelligence',
    icon: '🧠',
    commands: [
      { phrase: 'What opportunities am I missing?', description: 'Proactive insights generation' },
      { phrase: 'Analyze this contract for hidden risks', description: 'Contract analysis intelligence' },
      { phrase: 'Should I pursue this government contract?', description: 'AI decision support' },
      { phrase: 'Extract key terms from this contract', description: 'Document intelligence' },
      { phrase: 'Recommend pricing adjustments', description: 'Revenue optimization' },
    ]
  },
  {
    category: 'Market Intelligence (DDCSS)',
    icon: '💼',
    commands: [
      { phrase: 'Show me profitable market problems', description: 'Market problem search' },
      { phrase: 'Show me my most valuable problems', description: 'MVP scorecard' },
      { phrase: 'Show me competitor analysis', description: 'Competitive landscape' },
      { phrase: "What's the market size?", description: 'TAM/SAM analysis' },
    ]
  },
  {
    category: 'Learning & Memory',
    icon: '📚',
    commands: [
      { phrase: 'Let me teach you about my business', description: 'Share business knowledge' },
      { phrase: 'Remember this supplier didn\'t work out', description: 'Learn from outcomes' },
      { phrase: 'We\'re targeting this government agency', description: 'Strategic decision recording' },
      { phrase: 'Explain our business model', description: 'Business context review' },
    ]
  }
];

const AlexaSystem: React.FC<AlexaSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch('http://localhost:5001/alexa/health');
      const data = await res.json();
      setHealth(data);
    } catch {
      setHealth(null);
    }
    setLoading(false);
  };

  const testVoiceCommand = async (intentName: string) => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch('http://localhost:5001/alexa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request: { type: 'IntentRequest', intent: { name: intentName, slots: {} } }
        })
      });
      const data = await res.json();
      const ssml = data?.response?.outputSpeech?.ssml || data?.response?.outputSpeech?.text || 'No response';
      const clean = ssml.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      setTestResult(clean);
    } catch (err) {
      setTestResult('Error: Could not reach Alexa skill server');
    }
    setTesting(false);
  };

  const filteredCommands = VOICE_COMMANDS.map(cat => ({
    ...cat,
    commands: cat.commands.filter(cmd =>
      cmd.phrase.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cmd.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(cat => cat.commands.length > 0);

  const totalCommands = VOICE_COMMANDS.reduce((sum, cat) => sum + cat.commands.length, 0);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className={`rounded-xl p-4 border ${health ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${health ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <div>
              <div className="text-sm text-gray-400">Skill Server</div>
              <div className={`font-bold ${health ? 'text-green-400' : 'text-red-400'}`}>
                {loading ? 'Checking...' : health ? 'Online' : 'Offline'}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="text-2xl">🎙️</div>
            <div>
              <div className="text-sm text-gray-400">Voice Commands</div>
              <div className="font-bold text-blue-400">{health?.intents_handled || 98} Active</div>
            </div>
          </div>
        </div>

        <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="text-2xl">🌐</div>
            <div>
              <div className="text-sm text-gray-400">NEXUS API</div>
              <div className="font-bold text-purple-400">
                {health?.connected_to_nexus ? 'Connected' : 'Disconnected'}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="text-2xl">📡</div>
            <div>
              <div className="text-sm text-gray-400">Invocation</div>
              <div className="font-bold text-yellow-400">"Alexa, open Alexis NEXUS"</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {['commands', 'test', 'setup'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab === 'commands' && '🎙️ Voice Commands'}
            {tab === 'test' && '🧪 Test Lab'}
            {tab === 'setup' && '⚙️ Setup Info'}
          </button>
        ))}
      </div>

      {/* Voice Commands Tab */}
      {activeTab === 'commands' && (
        <div>
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search voice commands..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            />
            <div className="text-gray-500 text-sm mt-2">
              {totalCommands} voice commands across {VOICE_COMMANDS.length} categories
            </div>
          </div>

          <div className="space-y-3">
            {filteredCommands.map(category => (
              <div key={category.category} className="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpandedCategory(
                    expandedCategory === category.category ? null : category.category
                  )}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-700/50 transition"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{category.icon}</span>
                    <div className="text-left">
                      <div className="font-bold text-white">{category.category}</div>
                      <div className="text-sm text-gray-400">{category.commands.length} commands</div>
                    </div>
                  </div>
                  <span className="text-gray-400">
                    {expandedCategory === category.category ? '▼' : '▶'}
                  </span>
                </button>

                {expandedCategory === category.category && (
                  <div className="border-t border-gray-700">
                    {category.commands.map((cmd, i) => (
                      <div key={i} className="flex items-center justify-between px-4 py-3 hover:bg-gray-700/30 border-b border-gray-700/50 last:border-0">
                        <div className="flex-1">
                          <div className="text-blue-300 font-medium">"{cmd.phrase}"</div>
                          <div className="text-gray-500 text-sm">{cmd.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test Lab Tab */}
      {activeTab === 'test' && (
        <div>
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 mb-6">
            <h3 className="text-lg font-bold text-white mb-4">Quick Test</h3>
            <p className="text-gray-400 mb-4">Test voice commands directly from NEXUS. Click any button to simulate the command.</p>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { label: 'Daily Briefing', intent: 'GetExecutiveBriefing' },
                { label: 'Find Opportunities', intent: 'FindOpportunitiesIntent' },
                { label: 'Daily Target', intent: 'DailyTargetIntent' },
                { label: 'Pipeline Stats', intent: 'PipelineStatsIntent' },
                { label: 'Compliance Status', intent: 'GetComplianceLandscape' },
                { label: 'EDWOSB Set-Asides', intent: 'FindEDWOSBSetAsides' },
                { label: 'Micro-Purchases', intent: 'FindMicroPurchases' },
                { label: 'Bid Status', intent: 'GetBidWorkflowStatus' },
                { label: 'Sub Onboarding', intent: 'GetSubcontractorOnboardingStatus' },
                { label: 'Win/Loss Tracking', intent: 'GetWinLossTracking' },
                { label: 'Market Problems', intent: 'SearchMarketProblems' },
                { label: 'Proactive Insights', intent: 'ProactiveInsightsGeneration' },
              ].map(test => (
                <button
                  key={test.intent}
                  onClick={() => testVoiceCommand(test.intent)}
                  disabled={testing}
                  className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 px-4 py-3 rounded-lg text-sm font-medium transition text-left"
                >
                  {test.label}
                </button>
              ))}
            </div>
          </div>

          {testResult && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">🔊</span>
                <span className="font-bold text-blue-400">Alexa Response</span>
              </div>
              <p className="text-gray-300 leading-relaxed">{testResult}</p>
            </div>
          )}
        </div>
      )}

      {/* Setup Info Tab */}
      {activeTab === 'setup' && (
        <div className="space-y-6">
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Connection Details</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-400">Skill Name</span>
                <span className="text-white font-medium">NEXUS ALEXIS</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-400">Invocation</span>
                <span className="text-yellow-400 font-medium">"Alexa, open Alexis NEXUS"</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-400">Local Server</span>
                <span className="text-white font-mono text-sm">http://localhost:5001</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-400">NEXUS API</span>
                <span className="text-white font-mono text-sm">{health?.connected_to_nexus || 'http://localhost:8000'}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-700">
                <span className="text-gray-400">Intents Handled</span>
                <span className="text-blue-400 font-bold">{health?.intents_handled || '—'}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-gray-400">Status</span>
                <span className={`font-bold ${health ? 'text-green-400' : 'text-red-400'}`}>
                  {health ? 'Connected & Active' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">If Tunnel Disconnects</h3>
            <p className="text-gray-400 mb-4">
              The tunnel URL changes when your computer restarts. Run these commands to reconnect:
            </p>
            <pre className="bg-gray-900 rounded-lg p-4 text-sm text-green-400 overflow-x-auto">
{`cd "/Users/deedavis/NEXUS BACKEND"
source .venv/bin/activate
python nexus_alexa_skill.py &
cloudflared tunnel --url http://localhost:5001`}
            </pre>
            <p className="text-gray-500 text-sm mt-3">
              Then update the endpoint URL in the Alexa Developer Console under Endpoint → Default Region.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlexaSystem;
