import React, { useState } from 'react';

interface QuoteItem {
  number: string;
  description: string;
  specs: string;
  quantity: string;
  unit: string;
}

interface QuoteData {
  rfq_number: string;
  title: string;
  issue_date: string;
  due_date: string;
  due_time: string;
  contract_period: string;
  color_scheme: string;
  introduction: string;
  scope: string;
  requirements: string[];
  items: QuoteItem[];
}

export const QuoteGenerator: React.FC = () => {
  const [mode, setMode] = useState<'form' | 'paste'>('paste'); // Default to paste mode!
  const [pasteText, setPasteText] = useState('');
  
  const [quoteData, setQuoteData] = useState<QuoteData>({
    rfq_number: 'DDI-2026-001',
    title: '',
    issue_date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
    due_date: '',
    due_time: '5:00 PM EST',
    contract_period: '12 months',
    color_scheme: '1',
    introduction: 'DEE DAVIS INC is seeking competitive quotes for a Michigan municipal client.',
    scope: '',
    requirements: ['Competitive pricing required', 'Confirm delivery lead times'],
    items: [{ number: '1', description: '', specs: '', quantity: '', unit: 'unit' }]
  });

  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof QuoteData, value: any) => {
    setQuoteData({ ...quoteData, [field]: value });
  };

  const handleItemChange = (index: number, field: keyof QuoteItem, value: string) => {
    const newItems = [...quoteData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setQuoteData({ ...quoteData, items: newItems });
  };

  const addItem = () => {
    const newItems = [...quoteData.items];
    newItems.push({
      number: String(newItems.length + 1),
      description: '',
      specs: '',
      quantity: '',
      unit: 'unit'
    });
    setQuoteData({ ...quoteData, items: newItems });
  };

  const removeItem = (index: number) => {
    const newItems = quoteData.items.filter((_, i) => i !== index);
    setQuoteData({ ...quoteData, items: newItems });
  };

  const handlePasteGenerate = async () => {
    if (!pasteText.trim()) {
      setError('Please paste your quote information first!');
      return;
    }

    setGenerating(true);
    setError(null);
    setResult(null);

    try {
      // Send paste text directly to API
      const response = await fetch('http://localhost:5001/api/quote/generate-from-paste', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ paste_text: pasteText }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to generate quote');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerate = async () => {
    if (mode === 'paste') {
      handlePasteGenerate();
      return;
    }

    setGenerating(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5001/api/quote/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(quoteData),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to generate quote');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setGenerating(false);
    }
  };

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
2 | Another Item | Specs | Qty | unit
3 | Third Item | Details | Amount | unit`;
    
    setPasteText(template);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-8 rounded-lg mb-6">
        <h1 className="text-3xl font-bold mb-2">📋 Supplier Quote Request Generator</h1>
        <p className="text-blue-100">Generate professional quote requests for suppliers</p>
      </div>

      {/* Mode Selector */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('paste')}
          className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
            mode === 'paste'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📋 Paste Mode (Fastest!)
        </button>
        <button
          onClick={() => setMode('form')}
          className={`flex-1 py-3 px-6 rounded-lg font-semibold transition ${
            mode === 'form'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📝 Form Mode
        </button>
      </div>

      {/* Paste Mode */}
      {mode === 'paste' && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold mb-2 text-gray-800">
              Paste Your Quote Information
            </h2>
            <p className="text-gray-600 mb-4">
              Copy your quote template or info and paste below. Click "Load Template" for an example.
            </p>
            <button
              onClick={loadTemplate}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition mb-4"
            >
              📋 Load Template
            </button>
          </div>
          
          <textarea
            className="w-full h-96 px-4 py-3 border-2 border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500"
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
            placeholder="Paste your quote information here..."
          />

          <button
            onClick={handleGenerate}
            disabled={generating}
            className={`w-full mt-4 py-4 text-lg font-bold text-white rounded-lg transition ${
              generating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {generating ? '⚙️ Generating...' : '✨ Generate Quote Request'}
          </button>
        </div>
      )}

      {/* Form Mode */}
      {mode === 'form' && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        {/* RFQ Details */}
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4 text-gray-800">RFQ Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">RFQ Number</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={quoteData.rfq_number}
                onChange={(e) => handleInputChange('rfq_number', e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={quoteData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="e.g., Aggregate Materials - Annual Contract"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={quoteData.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
                placeholder="February 5, 2026"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Due Time</label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={quoteData.due_time}
                onChange={(e) => handleInputChange('due_time', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Introduction */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Introduction</label>
          <textarea
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            rows={3}
            value={quoteData.introduction}
            onChange={(e) => handleInputChange('introduction', e.target.value)}
            placeholder="Explain the purpose of this quote request..."
          />
        </div>

        {/* Scope */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Scope of Work</label>
          <textarea
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            rows={3}
            value={quoteData.scope}
            onChange={(e) => handleInputChange('scope', e.target.value)}
            placeholder="Describe what the vendor needs to provide..."
          />
        </div>

        {/* Items */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800">Items</h2>
            <button
              onClick={addItem}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              ➕ Add Item
            </button>
          </div>

          {quoteData.items.map((item, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-gray-700">Item #{item.number}</span>
                {quoteData.items.length > 1 && (
                  <button
                    onClick={() => removeItem(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    🗑️ Remove
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="Description"
                    value={item.description}
                    onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                  />
                </div>
                <div className="col-span-2">
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="Specifications"
                    value={item.specs}
                    onChange={(e) => handleItemChange(index, 'specs', e.target.value)}
                  />
                </div>
                <div>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="Quantity"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                  />
                </div>
                <div>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="Unit"
                    value={item.unit}
                    onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className={`w-full py-4 text-lg font-bold text-white rounded-lg transition ${
              generating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {generating ? '⚙️ Generating...' : '✨ Generate Quote Request'}
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          <h3 className="font-bold mb-2">✅ Quote Request Generated!</h3>
          <p className="mb-2">Your professional quote request is ready!</p>
          {result.download_url && (
            <a
              href={`http://localhost:5001${result.download_url}`}
              download
              className="inline-block px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
            >
              📥 Download PDF
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default QuoteGenerator;
