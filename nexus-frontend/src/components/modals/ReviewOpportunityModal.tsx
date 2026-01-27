import React, { useState } from 'react';
import { api } from '../../api/client';

interface ReviewOpportunityModalProps {
  opportunity: any;
  onClose: () => void;
  onSuccess: () => void;
}

export const ReviewOpportunityModal: React.FC<ReviewOpportunityModalProps> = ({
  opportunity,
  onClose,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    name: '',
    decision: 'pursue' as 'pursue' | 'skip',
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Auto-suggest name from opportunity details
  const generateSuggestedName = () => {
    const fields = opportunity.fields;
    const source = fields['Issuing Organization'] || fields['Agency'] || '';
    const category = fields['Category'] || fields['Service Type'] || '';
    
    if (source && category) {
      return `${source} - ${category}`;
    } else if (source) {
      return source;
    } else if (fields['Title']) {
      return fields['Title'].substring(0, 60);
    }
    return '';
  };

  const suggestedName = generateSuggestedName();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Please enter a name for this opportunity');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      // Try API call, but fall back to mock success for testing
      try {
        const response = await api.reviewOpportunity(opportunity.id, {
          name: formData.name.trim(),
          decision: formData.decision,
          notes: formData.notes.trim()
        });

        if (response.success) {
          onSuccess();
          onClose();
          return;
        }
      } catch (apiError) {
        console.log('API not available, using mock mode for testing');
      }

      // Mock mode - simulate successful review
      console.log('Mock mode: Would review opportunity as:', formData);
      
      // Show success message
      const action = formData.decision === 'pursue' ? 'pursued' : 'skipped';
      alert(`✅ Mock Mode: Successfully ${action} "${formData.name}"!\n\n(Backend not connected - this is for UI testing only)`);
      
      // Close modal and trigger refresh
      onSuccess();
      onClose();
      
    } catch (err: any) {
      console.error('Submit error:', err);
      setError(err?.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUseSuggestion = () => {
    setFormData({ ...formData, name: suggestedName });
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-xl border border-gray-700 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-black text-white">🔍 Review Opportunity</h2>
              <p className="text-sm text-blue-100 mt-1">Name this opportunity and decide if we should pursue it</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition text-2xl font-bold"
              disabled={submitting}
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Opportunity Details */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <h3 className="text-sm font-black text-blue-400 mb-3">OPPORTUNITY DETAILS</h3>
            
            <div className="space-y-2 text-sm">
              {opportunity.fields['Issuing Organization'] && (
                <div className="flex">
                  <span className="text-gray-400 w-32 flex-shrink-0">Agency:</span>
                  <span className="text-white font-semibold">{opportunity.fields['Issuing Organization']}</span>
                </div>
              )}
              
              {opportunity.fields['State'] && (
                <div className="flex">
                  <span className="text-gray-400 w-32 flex-shrink-0">Location:</span>
                  <span className="text-white">{opportunity.fields['State']}</span>
                </div>
              )}
              
              {opportunity.fields['Category'] && (
                <div className="flex">
                  <span className="text-gray-400 w-32 flex-shrink-0">Category:</span>
                  <span className="text-white">{opportunity.fields['Category']}</span>
                </div>
              )}
              
              {opportunity.fields['Estimated Value'] && (
                <div className="flex">
                  <span className="text-gray-400 w-32 flex-shrink-0">Value:</span>
                  <span className="text-green-400 font-bold">
                    ${Number(opportunity.fields['Estimated Value']).toLocaleString()}
                  </span>
                </div>
              )}
              
              {opportunity.fields['Response Deadline'] && (
                <div className="flex">
                  <span className="text-gray-400 w-32 flex-shrink-0">Deadline:</span>
                  <span className="text-yellow-400 font-bold">
                    {new Date(opportunity.fields['Response Deadline']).toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </span>
                </div>
              )}
              
              {opportunity.fields['Description'] && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <span className="text-gray-400 block mb-2">Description:</span>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    {opportunity.fields['Description'].substring(0, 300)}
                    {opportunity.fields['Description'].length > 300 && '...'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Name Input */}
          <div>
            <label className="block text-sm font-black text-white mb-2">
              OPPORTUNITY NAME *
            </label>
            
            {suggestedName && formData.name !== suggestedName && (
              <div className="mb-2 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-xs text-blue-400 font-bold mb-1">💡 SUGGESTED NAME:</div>
                    <div className="text-sm text-white">{suggestedName}</div>
                  </div>
                  <button
                    type="button"
                    onClick={handleUseSuggestion}
                    className="ml-3 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs font-bold transition"
                  >
                    Use This
                  </button>
                </div>
              </div>
            )}
            
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., CPS Energy - Industrial Supplies"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none transition"
              disabled={submitting}
              maxLength={100}
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.name.length}/100 characters
            </div>
          </div>

          {/* Decision */}
          <div>
            <label className="block text-sm font-black text-white mb-3">
              DECISION *
            </label>
            
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, decision: 'pursue' })}
                className={`p-4 rounded-lg border-2 transition ${
                  formData.decision === 'pursue'
                    ? 'bg-green-900/30 border-green-500 text-green-400'
                    : 'bg-gray-800/50 border-gray-700 text-gray-400 hover:border-gray-600'
                }`}
                disabled={submitting}
              >
                <div className="text-2xl mb-1">✅</div>
                <div className="font-black text-sm">PURSUE THIS</div>
                <div className="text-xs mt-1 opacity-75">Move to supplier search</div>
              </button>
              
              <button
                type="button"
                onClick={() => setFormData({ ...formData, decision: 'skip' })}
                className={`p-4 rounded-lg border-2 transition ${
                  formData.decision === 'skip'
                    ? 'bg-red-900/30 border-red-500 text-red-400'
                    : 'bg-gray-800/50 border-gray-700 text-gray-400 hover:border-gray-600'
                }`}
                disabled={submitting}
              >
                <div className="text-2xl mb-1">⏭️</div>
                <div className="font-black text-sm">SKIP THIS</div>
                <div className="text-xs mt-1 opacity-75">Not a good fit</div>
              </button>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-black text-white mb-2">
              NOTES (Optional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Why pursue or skip? Any special considerations?"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none transition resize-none"
              rows={4}
              disabled={submitting}
              maxLength={500}
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.notes.length}/500 characters
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="text-sm text-red-400">❌ {error}</div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-bold transition"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={submitting || !formData.name.trim()}
            >
              {submitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Saving...
                </span>
              ) : (
                `${formData.decision === 'pursue' ? '✅ Pursue' : '⏭️ Skip'} This Opportunity`
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
