import React, { useState } from 'react';

interface QuoteSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const QuoteSystem: React.FC<QuoteSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [mode, setMode] = useState<'paste' | 'form'>('paste');
  const [pasteText, setPasteText] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const loadTemplate = () => {
    const template = `RFQ_NUMBER: DDI-2026-001
TITLE: Quote Request Title
ISSUE_DATE: January 26, 2026
DUE_DATE: February 5, 2026
DUE_TIME: 5:00 PM EST
CONTRACT_PERIOD: 12 months

COLOR_SCHEME: 1

INTRODUCTION:
DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client.

SCOPE:
Vendor will provide materials as specified.

KEY_REQUIREMENTS:
- Competitive pricing required
- Fast delivery
- Net 30 terms

ITEMS:
1 | Item Description | Specifications | Quantity | unit
2 | Another Item | Specs | Qty | unit`;
    
    setPasteText(template);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    
    try {
      // Try real API first
      try {
        const response = await fetch('http://localhost:5001/api/quote/generate-from-paste', {
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
        message: 'Quote request generated successfully! (Mock Mode)',
        files: {
          pdf: 'mock-quote-request.pdf',
          html: 'mock-quote-request.html'
        },
        quote_data: {
          rfq_number: 'DDI-2026-001',
          title: 'Sample Quote Request',
          generated_at: new Date().toISOString()
        }
      };
      
      setResult(mockResult);
      
      alert('✅ Mock Mode: Quote Generated!\n\n📋 Your quote request has been "generated"\n📧 In production, this would:\n  • Create a PDF\n  • Save to Airtable\n  • Track timestamp\n  • Log supplier contact\n\n(Backend not connected - UI testing only)');
      
    } catch (error) {
      console.error('Error generating quote:', error);
      alert('❌ Error generating quote. Please check the console.');
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
              <h2 className="text-2xl font-bold text-blue-400 mb-4">Supplier Quote Requests</h2>
              <p className="text-gray-300 mb-6">
                Generate professional quote requests for suppliers. Automatically timestamped and tracked in Airtable.
              </p>

              {/* Mode selector */}
              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setMode('paste')}
                  className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                    mode === 'paste'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  📋 Paste Mode
                </button>
                <button
                  onClick={() => setMode('form')}
                  className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
                    mode === 'form'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  📝 Form Mode
                </button>
              </div>

              {mode === 'paste' && (
                <div>
                  <button
                    onClick={loadTemplate}
                    className="mb-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
                  >
                    📋 Load Template
                  </button>
                  
                  <textarea
                    className="w-full h-96 px-4 py-3 bg-gray-900 border-2 border-gray-700 rounded-lg font-mono text-sm text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={pasteText}
                    onChange={(e) => setPasteText(e.target.value)}
                    placeholder="Paste your quote information here..."
                  />

                  <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className={`w-full mt-4 py-4 text-lg font-bold rounded-lg transition ${
                      generating
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {generating ? '⚙️ Generating...' : '✨ Generate Quote Request'}
                  </button>

                  {result && result.success && (
                    <div className="mt-6 p-4 bg-green-900 border border-green-600 rounded-lg">
                      <h3 className="font-bold text-green-300 mb-2">✅ Quote Request Generated!</h3>
                      <p className="text-green-200 mb-3">Your professional quote request PDF is ready!</p>
                      
                      {result.download_url ? (
                        <a
                          href={`http://localhost:5001${result.download_url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition"
                        >
                          📥 Download PDF
                        </a>
                      ) : (
                        <p className="text-sm text-green-300">(Mock mode - no actual file generated)</p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {mode === 'form' && (
                <div className="text-center py-12 text-gray-400">
                  <p>Form mode coming soon!</p>
                  <p className="text-sm">Use Paste Mode for now - it's faster anyway! 😊</p>
                </div>
              )}
            </div>
          </div>
        );

      case 'tracking':
        return (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-blue-400 mb-4">Quote Request Tracking</h2>
            <p className="text-gray-300">Track all sent quote requests with timestamps and follow-ups.</p>
            <div className="mt-6 text-center text-gray-400">
              <p>Airtable integration coming soon...</p>
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
            className="mb-4 text-blue-400 hover:text-blue-300 transition"
          >
            ← Back to NEXUS
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
            Supplier Quote System
          </h1>
          <p className="text-gray-400 mt-2">Generate and track supplier quote requests</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'dashboard'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Generate Quotes
          </button>
          <button
            onClick={() => setActiveTab('tracking')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'tracking'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Track Requests
          </button>
        </div>

        {/* Content */}
        {renderContent()}
      </div>
    </div>
  );
};

export default QuoteSystem;
