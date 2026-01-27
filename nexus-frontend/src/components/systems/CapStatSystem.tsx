import React, { useState } from 'react';

interface CapStatSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const CapStatSystem: React.FC<CapStatSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [pasteText, setPasteText] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const loadTemplate = () => {
    const template = `CLIENT_NAME: Client Name Here
RFQ_NUMBER: RFQ-123456
DATE: January 2026

COLOR_SCHEME: 1
(1=Navy/Gold, 2=Blue/Teal, 3=Brown/Orange, 4=Purple/Violet, 5=Corporate Blue, 6=Green)

OVERVIEW:
DEE DAVIS INC specializes in supply chain management and logistics for government clients. Paste your company overview here...

HIGHLIGHTS:
NAICS: 423850 - Industrial Supplies
Partners: Partner1 | Partner2 | Partner3
Performance: 98%+ On-Time Delivery
Coverage: Nationwide sourcing with Michigan delivery`;
    
    setPasteText(template);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    
    try {
      // Try real API first
      try {
        const response = await fetch('http://localhost:5000/api/capstat/generate-from-paste', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ paste_text: pasteText })
        });

        if (response.ok) {
          const data = await response.json();
          setResult(data);
          setGenerating(false);
          return;
        }
      } catch (apiError) {
        console.log('API not available, using mock mode');
      }

      // Mock mode - simulate successful generation
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing
      
      const mockResult = {
        success: true,
        message: 'Capability Statement generated successfully! (Mock Mode)',
        files: {
          pdf: 'mock-capability-statement.pdf',
          html: 'mock-capability-statement.html'
        },
        capstat_data: {
          company_name: 'Dee Davis Inc.',
          template_used: 'Default Professional',
          generated_at: new Date().toISOString()
        }
      };
      
      setResult(mockResult);
      
      alert('✅ Mock Mode: Capability Statement Generated!\n\n📄 Your capability statement has been "generated"\n📧 In production, this would:\n  • Create a professional PDF\n  • Apply your branding\n  • Include all certifications\n  • Ready to attach to bids\n\n(Backend not connected - UI testing only)');
      
    } catch (error) {
      console.error('Error generating capability statement:', error);
      alert('❌ Error generating capability statement. Please check the console.');
    } finally {
      setGenerating(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-purple-400 mb-4">Capability Statement Generator</h2>
              <p className="text-gray-300 mb-6">
                Generate professional capability statements for government bids and client presentations.
              </p>

              <button
                onClick={loadTemplate}
                className="mb-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
              >
                📋 Load Template
              </button>
              
              <textarea
                className="w-full h-96 px-4 py-3 bg-gray-900 border-2 border-gray-700 rounded-lg font-mono text-sm text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={pasteText}
                onChange={(e) => setPasteText(e.target.value)}
                placeholder="Paste your capability statement information here..."
              />

              <button
                onClick={handleGenerate}
                disabled={generating}
                className={`w-full mt-4 py-4 text-lg font-bold rounded-lg transition ${
                  generating
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }`}
              >
                {generating ? '⚙️ Generating...' : '✨ Generate Capability Statement'}
              </button>

              {result && result.success && (
                <div className="mt-6 p-4 bg-purple-900 border border-purple-600 rounded-lg">
                  <h3 className="font-bold text-purple-300 mb-2">✅ Capability Statement Generated!</h3>
                  <p className="text-purple-200">Your professional capability statement PDF is ready!</p>
                </div>
              )}
            </div>
          </div>
        );

      case 'templates':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-purple-400 mb-4">Saved Templates</h2>
            <p className="text-gray-300">Manage your capability statement templates for different clients and industries.</p>
            <div className="mt-6 text-center text-gray-400">
              <p>Template library coming soon...</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBackToNexus}
            className="mb-4 text-purple-400 hover:text-purple-300 transition"
          >
            ← Back to NEXUS
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
            Capability Statement System
          </h1>
          <p className="text-gray-400 mt-2">Generate professional capability statements for bids</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'dashboard'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Generate
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'templates'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Templates
          </button>
        </div>

        {/* Content */}
        {renderContent()}
      </div>
    </div>
  );
};

export default CapStatSystem;
