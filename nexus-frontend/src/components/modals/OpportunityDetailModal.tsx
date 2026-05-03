import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface OpportunityDetailModalProps {
  recordId: string;
  onClose: () => void;
  onOpenInGPSS: () => void;
}

interface OpportunityDetails {
  id: string;
  name: string;
  notice_id: string;
  solicitation_number: string;
  agency: string;
  department: string;
  description: string;
  naics_codes: string;
  set_aside: string;
  deadline: string;
  posted_date: string;
  status: string;
  estimated_value: string;
  place_of_performance: string;
  co_name: string;
  co_email: string;
  co_phone: string;
  sam_url: string;
  source_url: string;
  attachments: string[];
  notes: string;
}

export const OpportunityDetailModal: React.FC<OpportunityDetailModalProps> = ({
  recordId,
  onClose,
  onOpenInGPSS,
}) => {
  const [loading, setLoading] = useState(true);
  const [details, setDetails] = useState<OpportunityDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const response = await api.getOpportunityDetails(recordId);
        if (response.success) {
          setDetails(response.opportunity);
        } else {
          setError(response.error || 'Failed to load opportunity details');
        }
      } catch (err) {
        setError('Failed to fetch opportunity details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [recordId]);

  const handleGenerateCapStatement = async () => {
    if (!details) return;
    setActionLoading('cap');
    try {
      const response = await api.generateCapabilityStatement(recordId);
      if (response.success) {
        alert('Capability statement generated! Check SEND_TO_BUYER folder.');
      } else {
        alert('Failed to generate: ' + (response.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Error generating capability statement');
    } finally {
      setActionLoading(null);
    }
  };

  const handleEmailCO = () => {
    if (!details?.co_email) {
      alert('No CO email available for this opportunity');
      return;
    }
    const subject = encodeURIComponent(`EDWOSB Interest — ${details.name}`);
    const body = encodeURIComponent(
      `Dear ${details.co_name || 'Contracting Officer'},\n\n` +
      `I am writing to express Dee Davis Inc.'s interest in ${details.solicitation_number || details.notice_id || 'your solicitation'}.\n\n` +
      `Dee Davis Inc. is a certified EDWOSB, Michigan-based contract management firm...\n\n` +
      `Best regards,\nDieasha D. Davis\nPresident & CEO\nDee Davis Inc.\n248.376.4550 | info@deedavis.biz`
    );
    window.open(`mailto:${details.co_email}?subject=${subject}&body=${body}`, '_blank');
  };

  const handleAddToCalendar = () => {
    if (!details?.deadline) {
      alert('No deadline available for this opportunity');
      return;
    }
    const title = encodeURIComponent(`🔥 BID DUE: ${details.name}`);
    const deadlineDate = new Date(details.deadline);
    const startDate = deadlineDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    const endDate = new Date(deadlineDate.getTime() + 3600000).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    const calUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startDate}/${endDate}&details=${encodeURIComponent(details.description || '')}`;
    window.open(calUrl, '_blank');
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'Not specified';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const getDaysUntilDeadline = (deadline: string) => {
    if (!deadline) return null;
    const now = new Date();
    const due = new Date(deadline);
    const diffMs = due.getTime() - now.getTime();
    const days = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl border border-gray-700 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700 bg-gray-800/50">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📋</span>
            <h2 className="text-xl font-bold text-white">Opportunity Details</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition p-2 hover:bg-gray-700 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              <span className="ml-4 text-gray-400">Loading opportunity details...</span>
            </div>
          ) : error ? (
            <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-6 text-center">
              <span className="text-red-400">{error}</span>
            </div>
          ) : details ? (
            <div className="space-y-6">
              {/* Title & Status */}
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">{details.name}</h3>
                <div className="flex flex-wrap gap-2">
                  {details.set_aside && (
                    <span className="px-3 py-1 bg-emerald-900/50 text-emerald-300 rounded-full text-sm font-semibold">
                      {details.set_aside}
                    </span>
                  )}
                  {details.status && (
                    <span className="px-3 py-1 bg-blue-900/50 text-blue-300 rounded-full text-sm font-semibold">
                      {details.status}
                    </span>
                  )}
                </div>
              </div>

              {/* Deadline Alert */}
              {details.deadline && (
                <div className={`p-4 rounded-lg border ${
                  getDaysUntilDeadline(details.deadline)! <= 3
                    ? 'bg-red-900/30 border-red-500/50'
                    : getDaysUntilDeadline(details.deadline)! <= 7
                    ? 'bg-amber-900/30 border-amber-500/50'
                    : 'bg-blue-900/30 border-blue-500/50'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-lg font-bold text-white">⏰ Response Deadline</span>
                      <p className="text-xl font-mono text-white mt-1">{formatDate(details.deadline)}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-3xl font-black ${
                        getDaysUntilDeadline(details.deadline)! <= 3
                          ? 'text-red-400'
                          : getDaysUntilDeadline(details.deadline)! <= 7
                          ? 'text-amber-400'
                          : 'text-blue-400'
                      }`}>
                        {getDaysUntilDeadline(details.deadline)} days
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Key Info Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoCard label="Notice ID" value={details.notice_id} copyable />
                <InfoCard label="Solicitation #" value={details.solicitation_number} copyable />
                <InfoCard label="Agency" value={details.agency || details.department} />
                <InfoCard label="NAICS" value={details.naics_codes} />
                <InfoCard label="Estimated Value" value={details.estimated_value} />
                <InfoCard label="Place of Performance" value={details.place_of_performance} />
                <InfoCard label="Posted Date" value={formatDate(details.posted_date)} />
                <InfoCard label="Source" value={details.sam_url ? 'SAM.gov' : 'Other'} />
              </div>

              {/* CO Contact */}
              {(details.co_name || details.co_email || details.co_phone) && (
                <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                    <span>👤</span> Contracting Officer
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {details.co_name && (
                      <div>
                        <span className="text-gray-400 text-sm">Name</span>
                        <p className="text-white font-semibold">{details.co_name}</p>
                      </div>
                    )}
                    {details.co_email && (
                      <div>
                        <span className="text-gray-400 text-sm">Email</span>
                        <a href={`mailto:${details.co_email}`} className="text-blue-400 hover:text-blue-300 font-semibold block">
                          {details.co_email}
                        </a>
                      </div>
                    )}
                    {details.co_phone && (
                      <div>
                        <span className="text-gray-400 text-sm">Phone</span>
                        <a href={`tel:${details.co_phone}`} className="text-blue-400 hover:text-blue-300 font-semibold block">
                          {details.co_phone}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Description */}
              {details.description && (
                <div>
                  <h4 className="text-lg font-bold text-white mb-2">Description</h4>
                  <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-300 whitespace-pre-wrap">{details.description}</p>
                  </div>
                </div>
              )}

              {/* SAM.gov Link */}
              {(details.sam_url || details.source_url) && (
                <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/30">
                  <a
                    href={details.sam_url || details.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 text-blue-400 hover:text-blue-300 font-semibold"
                  >
                    <span className="text-xl">🔗</span>
                    <span>View Full Solicitation on SAM.gov</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              )}

              {/* Notes */}
              {details.notes && (
                <div>
                  <h4 className="text-lg font-bold text-white mb-2">Notes</h4>
                  <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                    <p className="text-gray-300 whitespace-pre-wrap">{details.notes}</p>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Action Footer */}
        {details && !loading && (
          <div className="border-t border-gray-700 p-4 bg-gray-800/50">
            <div className="flex flex-wrap gap-3 justify-between">
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleGenerateCapStatement}
                  disabled={actionLoading === 'cap'}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-600 text-white font-bold rounded-lg transition flex items-center gap-2"
                >
                  {actionLoading === 'cap' ? (
                    <span className="animate-spin">⏳</span>
                  ) : (
                    <span>📄</span>
                  )}
                  Generate Cap Statement
                </button>
                {details.co_email && (
                  <button
                    onClick={handleEmailCO}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition flex items-center gap-2"
                  >
                    <span>✉️</span>
                    Email CO
                  </button>
                )}
                {details.deadline && (
                  <button
                    onClick={handleAddToCalendar}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg transition flex items-center gap-2"
                  >
                    <span>📅</span>
                    Add to Calendar
                  </button>
                )}
              </div>
              <button
                onClick={onOpenInGPSS}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg transition flex items-center gap-2"
              >
                <span>🚀</span>
                Open in GPSS
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper component for info cards
const InfoCard: React.FC<{ label: string; value: string | undefined; copyable?: boolean }> = ({
  label,
  value,
  copyable,
}) => {
  const handleCopy = () => {
    if (value) {
      navigator.clipboard.writeText(value);
    }
  };

  return (
    <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
      <span className="text-gray-400 text-xs uppercase tracking-wide">{label}</span>
      <div className="flex items-center justify-between mt-1">
        <p className="text-white font-semibold truncate">{value || 'Not specified'}</p>
        {copyable && value && (
          <button
            onClick={handleCopy}
            className="text-gray-400 hover:text-white ml-2 p-1"
            title="Copy to clipboard"
          >
            📋
          </button>
        )}
      </div>
    </div>
  );
};

export default OpportunityDetailModal;
