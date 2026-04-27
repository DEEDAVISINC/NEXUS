import React, { useState, useEffect } from 'react';

const SESSION_KEY = 'shield_hipaa_ack';

function hasAcknowledged(): boolean {
  try { return sessionStorage.getItem(SESSION_KEY) === '1'; } catch { return false; }
}

function setAcknowledged(): void {
  try { sessionStorage.setItem(SESSION_KEY, '1'); } catch { /* ignore */ }
}

interface HIPAAGateProps {
  children: React.ReactNode;
}

const HIPAAGate: React.FC<HIPAAGateProps> = ({ children }) => {
  const [acked, setAcked] = useState(hasAcknowledged);

  useEffect(() => {
    setAcked(hasAcknowledged());
  }, []);

  if (acked) return <>{children}</>;

  return (
    <div className="fixed inset-0 z-[9999] bg-[#050f2e] flex items-center justify-center px-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#f5c23e]/15 border border-[#f5c23e]/40 mb-4">
            <span className="text-3xl">🛡️</span>
          </div>
          <h1 className="text-2xl font-black text-white">SHIELD Compliance Notice</h1>
          <p className="text-sm text-[#8ea2d6] mt-1">DEE DAVIS INC + CAUSE WE CARE</p>
        </div>

        {/* Compliance Card */}
        <div className="bg-[#081849] border border-[#1c2f6a] rounded-xl overflow-hidden">
          <div className="bg-red-500/10 border-b border-red-500/30 px-6 py-3">
            <div className="text-xs font-black text-red-400 uppercase tracking-wider">
              HIPAA / PII / PHI — Protected Information
            </div>
          </div>

          <div className="px-6 py-5 space-y-4">
            <p className="text-sm text-slate-200 leading-relaxed">
              This system contains <span className="text-white font-bold">Protected Health Information (PHI)</span>,{' '}
              <span className="text-white font-bold">Personally Identifiable Information (PII)</span>,{' '}
              and data governed by <span className="text-white font-bold">HIPAA</span> regulations.
            </p>

            <div className="bg-[#050f2e] border border-[#1c2f6a] rounded-lg p-4 space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-[#f5c23e] font-bold text-sm mt-0.5">1.</span>
                <p className="text-xs text-[#c4d4f0] leading-relaxed">
                  <span className="text-white font-semibold">Access is restricted</span> to authorized personnel with a
                  legitimate need to view, process, or manage client records related to lead screening, referrals,
                  and MDHHS services.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#f5c23e] font-bold text-sm mt-0.5">2.</span>
                <p className="text-xs text-[#c4d4f0] leading-relaxed">
                  <span className="text-white font-semibold">Do not share, screenshot, or export</span> any client data —
                  including names, addresses, phone numbers, BLL results, medical records, or case details — except
                  through approved SHIELD workflows.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#f5c23e] font-bold text-sm mt-0.5">3.</span>
                <p className="text-xs text-[#c4d4f0] leading-relaxed">
                  <span className="text-white font-semibold">All activity is logged.</span> Access, edits, exports,
                  and communications are recorded for HIPAA audit compliance under 45 CFR § 164.312.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#f5c23e] font-bold text-sm mt-0.5">4.</span>
                <p className="text-xs text-[#c4d4f0] leading-relaxed">
                  <span className="text-white font-semibold">Violations are reportable.</span> Unauthorized access or
                  disclosure of PHI may result in disciplinary action, termination, and civil/criminal penalties
                  under HIPAA (up to $250,000 and 10 years imprisonment).
                </p>
              </div>
            </div>

            <div className="bg-[#f5c23e]/10 border border-[#f5c23e]/30 rounded-lg px-4 py-3">
              <p className="text-xs text-[#fcd75a] leading-relaxed">
                <span className="font-bold">Michigan PA 146 of 2023:</span> SHIELD operates under the universal
                blood lead screening mandate. Family data, BLL results, CLPPP referrals, and navigator case notes
                are PHI and must be handled in full compliance with state and federal privacy law.
              </p>
            </div>
          </div>

          <div className="px-6 py-4 border-t border-[#1c2f6a] bg-[#050f2e]/60">
            <button
              onClick={() => { setAcknowledged(); setAcked(true); }}
              className="w-full bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] py-3 rounded-xl text-sm font-black transition-all"
            >
              I Acknowledge — Proceed to SHIELD
            </button>
            <p className="text-center text-[10px] text-[#6b7ba6] mt-3">
              This acknowledgment is valid for the current browser session.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HIPAAGate;
