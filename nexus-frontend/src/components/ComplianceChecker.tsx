import React, { useState } from 'react';
import { api } from '../api/client';

interface ComplianceCheckerProps {
  rfpContent: string;
  proposalData: any;
  onClose: () => void;
}

interface ComplianceIssue {
  type: string;
  item: string;
  message: string;
  fix: string;
}

interface ComplianceCheck {
  compliance_score: number;
  risk_level: string;
  critical_issues: number;
  total_issues: number;
  total_warnings: number;
  issues: ComplianceIssue[];
  warnings: ComplianceIssue[];
  compliant_items: string[];
  summary: string;
}

const ComplianceChecker: React.FC<ComplianceCheckerProps> = ({
  rfpContent,
  proposalData,
  onClose
}) => {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [rfpRequirements, setRfpRequirements] = useState<any>(null);
  const [complianceCheck, setComplianceCheck] = useState<ComplianceCheck | null>(null);
  const [report, setReport] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const analyzeRfp = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const requirements = await api.analyzeRfpCompliance(rfpContent);
      
      if (requirements.error) {
        setError(requirements.error);
      } else {
        setRfpRequirements(requirements);
        // Automatically check compliance after analyzing RFP
        await checkCompliance(requirements);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze RFP');
    } finally {
      setAnalyzing(false);
    }
  };

  const checkCompliance = async (requirements?: any) => {
    setLoading(true);
    setError(null);
    try {
      const reqs = requirements || rfpRequirements;
      if (!reqs) {
        setError('Please analyze RFP first');
        return;
      }

      const result = await api.checkProposalCompliance(proposalData, reqs);
      
      if (result.error) {
        setError(result.error);
      } else {
        setComplianceCheck(result.compliance_check);
        setReport(result.report);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to check compliance');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    if (riskLevel.includes('HIGH')) return 'text-red-400 bg-red-500/20 border-red-500';
    if (riskLevel.includes('MEDIUM')) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500';
    if (riskLevel.includes('LOW')) return 'text-orange-400 bg-orange-500/20 border-orange-500';
    return 'text-green-400 bg-green-500/20 border-green-500';
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
      <div className="bg-gray-800 rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 sticky top-0 z-10">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">✅ Proposal Compliance Checker</h2>
              <p className="text-white/80">Prevent rejection due to non-compliance</p>
            </div>
            <button 
              onClick={onClose}
              className="text-white hover:text-gray-300 text-3xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {!rfpRequirements && !analyzing && !complianceCheck && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-xl font-bold mb-4">RFP Compliance Analysis</h3>
              <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
                Our AI will analyze the RFP to extract all compliance requirements, evaluation factors, 
                and critical submission items. Then it will check your proposal against these requirements.
              </p>
              <button 
                onClick={analyzeRfp}
                className="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-lg font-bold text-lg transition"
              >
                🔍 Analyze RFP & Check Compliance
              </button>
            </div>
          )}

          {analyzing && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 animate-pulse">🤖</div>
              <h3 className="text-xl font-bold mb-2">Analyzing RFP Requirements...</h3>
              <p className="text-gray-400">
                Extracting submission requirements, evaluation factors, and compliance items...
              </p>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 animate-pulse">✅</div>
              <h3 className="text-xl font-bold mb-2">Checking Proposal Compliance...</h3>
              <p className="text-gray-400">
                Comparing your proposal against RFP requirements...
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/30 border border-red-600 rounded-xl p-6 text-center">
              <p className="text-red-400 font-semibold">❌ {error}</p>
              <button 
                onClick={analyzeRfp}
                className="mt-4 bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-semibold transition"
              >
                Try Again
              </button>
            </div>
          )}

          {complianceCheck && (
            <div className="space-y-6">
              {/* Compliance Score Banner */}
              <div className={`border-2 rounded-xl p-6 ${getRiskColor(complianceCheck.risk_level)}`}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Compliance Score</h3>
                    <div className={`text-6xl font-black ${getScoreColor(complianceCheck.compliance_score)}`}>
                      {complianceCheck.compliance_score}%
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400 mb-2">Risk Level</div>
                    <div className="text-2xl font-bold">{complianceCheck.risk_level}</div>
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-4 text-center text-sm">
                  <div>
                    <div className="text-2xl font-bold">{complianceCheck.critical_issues}</div>
                    <div className="text-gray-400">Critical Issues</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{complianceCheck.total_issues}</div>
                    <div className="text-gray-400">Total Issues</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{complianceCheck.total_warnings}</div>
                    <div className="text-gray-400">Warnings</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{complianceCheck.compliant_items.length}</div>
                    <div className="text-gray-400">Compliant Items</div>
                  </div>
                </div>
              </div>

              {/* Critical Issues */}
              {complianceCheck.critical_issues > 0 && (
                <div className="bg-red-900/30 border border-red-600 rounded-xl p-6">
                  <h3 className="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
                    <span>🚨</span> CRITICAL ISSUES (Will Cause Rejection)
                  </h3>
                  <div className="space-y-4">
                    {complianceCheck.issues.filter(i => i.type === 'CRITICAL').map((issue, index) => (
                      <div key={index} className="bg-red-900/20 p-4 rounded-lg border border-red-700">
                        <div className="font-bold text-red-400 mb-2">❌ {issue.item}</div>
                        <div className="text-gray-300 text-sm mb-2">{issue.message}</div>
                        <div className="text-green-400 text-sm">
                          <span className="font-semibold">Fix:</span> {issue.fix}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Major Issues */}
              {complianceCheck.total_issues > complianceCheck.critical_issues && (
                <div className="bg-yellow-900/30 border border-yellow-600 rounded-xl p-6">
                  <h3 className="text-xl font-bold text-yellow-400 mb-4 flex items-center gap-2">
                    <span>⚠️</span> MAJOR ISSUES (Will Lose Points)
                  </h3>
                  <div className="space-y-4">
                    {complianceCheck.issues.filter(i => i.type !== 'CRITICAL').map((issue, index) => (
                      <div key={index} className="bg-yellow-900/20 p-4 rounded-lg border border-yellow-700">
                        <div className="font-bold text-yellow-400 mb-2">⚠️ {issue.item}</div>
                        <div className="text-gray-300 text-sm mb-2">{issue.message}</div>
                        <div className="text-green-400 text-sm">
                          <span className="font-semibold">Fix:</span> {issue.fix}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Warnings */}
              {complianceCheck.warnings.length > 0 && (
                <div className="bg-blue-900/30 border border-blue-600 rounded-xl p-6">
                  <h3 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
                    <span>💡</span> Warnings & Recommendations
                  </h3>
                  <div className="space-y-3">
                    {complianceCheck.warnings.map((warning, index) => (
                      <div key={index} className="flex items-start gap-3 text-sm">
                        <span className="text-blue-400 font-bold">•</span>
                        <div>
                          <span className="font-semibold text-blue-400">{warning.item}:</span>
                          <span className="text-gray-300"> {warning.message}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Compliant Items */}
              <div className="bg-green-900/30 border border-green-600 rounded-xl p-6">
                <h3 className="text-xl font-bold text-green-400 mb-4 flex items-center gap-2">
                  <span>✅</span> Compliant Items ({complianceCheck.compliant_items.length})
                </h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {complianceCheck.compliant_items.map((item, index) => (
                    <div key={index} className="flex items-center gap-2 text-gray-300">
                      <span className="text-green-400">✓</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Text Report */}
              <div className="bg-gray-700 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">📄 Detailed Report</h3>
                <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono bg-gray-900 p-4 rounded-lg overflow-x-auto">
                  {report}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-700 p-6 flex gap-4 justify-end sticky bottom-0">
          <button 
            onClick={onClose}
            className="bg-gray-600 hover:bg-gray-500 px-6 py-3 rounded-lg font-semibold transition"
          >
            Close
          </button>
          {complianceCheck && complianceCheck.critical_issues === 0 && (
            <button 
              onClick={onClose}
              className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition"
            >
              ✓ Proceed with Proposal
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComplianceChecker;

