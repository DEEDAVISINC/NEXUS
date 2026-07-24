import React, { useCallback, useEffect, useState } from 'react';
import { api, VOICE_API_BASE } from '../../api/client';

interface VoiceStatus {
  enabled: boolean;
  twilio_configured: boolean;
  openai_configured: boolean;
  elevenlabs_configured?: boolean;
  tts_provider?: string;
  tts_voice?: string;
  transfer_number_masked?: string;
  webhook_base_url?: string;
  inbound_webhook?: string;
  gather_webhook?: string;
  default_flow?: string;
}

interface VoiceCallRecord {
  call_sid: string;
  caller?: string;
  flow?: string;
  status: string;
  confirmation?: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

interface PrismVoiceCallCenterProps {
  accent: string;
}

function ttsProviderLabel(provider?: string): string {
  if (!provider) return '—';
  if (provider === 'elevenlabs') return 'ElevenLabs';
  if (provider === 'twilio_generative') return 'Twilio generative';
  if (provider === 'twilio_neural') return 'Twilio neural';
  return provider.replace(/_/g, ' ');
}

const PrismVoiceCallCenter: React.FC<PrismVoiceCallCenterProps> = ({ accent }) => {
  const [status, setStatus] = useState<VoiceStatus | null>(null);
  const [calls, setCalls] = useState<VoiceCallRecord[]>([]);
  const [activeSessions, setActiveSessions] = useState(0);
  const [loading, setLoading] = useState(true);
  const [simSpeech, setSimSpeech] = useState('');
  const [simCallSid, setSimCallSid] = useState('');
  const [simResult, setSimResult] = useState('');
  const [simBusy, setSimBusy] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [st, log] = await Promise.all([
        api.getPrismVoiceStatus(),
        api.getPrismVoiceCalls(50),
      ]);
      setStatus(st);
      setCalls(log.calls || []);
      setActiveSessions(log.active_sessions || 0);
    } catch (e) {
      console.error('Voice center load failed', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 30000);
    return () => clearInterval(t);
  }, [refresh]);

  const runSim = async () => {
    if (!simSpeech.trim()) return;
    setSimBusy(true);
    try {
      const res = await api.simulatePrismVoiceCall({
        call_sid: simCallSid || undefined,
        speech: simSpeech.trim(),
        caller: '+12483764550',
      });
      if (res.call_sid) setSimCallSid(res.call_sid);
      setSimResult(res.prompt || JSON.stringify(res));
      if (res.confirmation) {
        setSimSpeech('');
        refresh();
      }
    } catch (e: unknown) {
      setSimResult(e instanceof Error ? e.message : 'Simulation failed');
    } finally {
      setSimBusy(false);
    }
  };

  const resetSim = () => {
    setSimCallSid('');
    setSimSpeech('');
    setSimResult('');
  };

  const statusColor = (s: string) => {
    if (s === 'completed') return '#6EE7B7';
    if (s === 'error') return '#FCA5A5';
    if (s === 'started' || s === 'in_progress') return '#93C5FD';
    return '#9CA3AF';
  };

  const elevenLabsActive =
    status?.tts_provider === 'elevenlabs' || Boolean(status?.elevenlabs_configured);
  const liveTtsLabel = ttsProviderLabel(status?.tts_provider);

  const statusCards: Array<{
    label: string;
    headline: string;
    hint: string;
    color: string;
    border?: string;
  }> = [
    {
      label: 'Twilio',
      headline: status?.twilio_configured ? 'Ready' : 'Setup needed',
      hint: '855 member line · live calls',
      color: status?.twilio_configured ? '#6EE7B7' : '#FCA5A5',
    },
    {
      label: 'Live voice',
      headline: elevenLabsActive ? 'Active' : liveTtsLabel,
      hint: elevenLabsActive
        ? `ElevenLabs · fallback ${status?.tts_voice || 'Twilio generative'}`
        : liveTtsLabel,
      color: elevenLabsActive ? accent : '#93C5FD',
      border: elevenLabsActive ? `2px solid ${accent}55` : undefined,
    },
    {
      label: 'ElevenLabs',
      headline: elevenLabsActive ? 'Active' : status?.elevenlabs_configured ? 'Ready' : 'Not configured',
      hint: elevenLabsActive
        ? 'Premium human voice on live calls'
        : status?.elevenlabs_configured
          ? 'Key present — check PA env'
          : 'Add ELEVENLABS_API_KEY on PythonAnywhere',
      color: elevenLabsActive ? '#6EE7B7' : status?.elevenlabs_configured ? '#6EE7B7' : '#FCA5A5',
      border: elevenLabsActive ? '2px solid rgba(16,185,129,0.35)' : undefined,
    },
    {
      label: 'OpenAI',
      headline: status?.openai_configured ? 'Ready' : 'Optional',
      hint: status?.openai_configured ? 'Speech parsing' : 'Parsing works without it',
      color: status?.openai_configured ? '#6EE7B7' : '#9CA3AF',
    },
    {
      label: 'Active calls',
      headline: String(activeSessions),
      hint: activeSessions > 0 ? 'In progress now' : 'No live sessions',
      color: activeSessions > 0 ? accent : '#9CA3AF',
    },
  ];

  return (
    <div style={{ padding: 24, maxWidth: 960 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24, gap: 16, flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: '#F9FAFB', margin: 0 }}>Voice Intake — Call Center</h2>
          <p style={{ fontSize: 13, color: 'rgba(156,163,175,0.8)', marginTop: 6, maxWidth: 560 }}>
            HAP CareSource members call in → AI collects trip details → creates PRISM + NEMT orders automatically.
          </p>
          <p style={{ fontSize: 11, color: 'rgba(107,114,128,0.85)', marginTop: 8 }}>
            Status from <code style={{ color: '#A5B4FC' }}>{VOICE_API_BASE}</code>
            {elevenLabsActive && (
              <span style={{ marginLeft: 10, color: '#6EE7B7', fontWeight: 700 }}>· ElevenLabs active on production</span>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={refresh}
          style={{ padding: '8px 14px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.12)', background: 'rgba(255,255,255,0.04)', color: '#E5E7EB', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
        >
          Refresh
        </button>
      </div>

      {elevenLabsActive && (
        <div
          style={{
            background: 'rgba(16,185,129,0.1)',
            border: '1px solid rgba(52,211,153,0.35)',
            borderRadius: 10,
            padding: '12px 14px',
            marginBottom: 16,
            fontSize: 13,
            color: '#A7F3D0',
          }}
        >
          <strong style={{ color: '#6EE7B7' }}>Active: ElevenLabs</strong>
          {' — '}Callers hear natural voice audio on <strong>855-773-0035</strong>. Twilio generative is fallback only.
        </div>
      )}

      {/* Status cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12, marginBottom: 24 }}>
        {statusCards.map((c) => (
          <div
            key={c.label}
            style={{
              background: '#14141A',
              border: c.border || '1px solid rgba(255,255,255,0.06)',
              borderRadius: 12,
              padding: 16,
            }}
          >
            <p style={{ fontSize: 10, fontWeight: 700, color: 'rgba(107,114,128,0.8)', textTransform: 'uppercase', letterSpacing: 0.8, margin: 0 }}>{c.label}</p>
            <p style={{ fontSize: 18, fontWeight: 800, color: c.color, margin: '6px 0 2px' }}>{c.headline}</p>
            <p style={{ fontSize: 11, color: 'rgba(156,163,175,0.6)', margin: 0 }}>{c.hint}</p>
          </div>
        ))}
      </div>

      {status?.inbound_webhook && (
        <div style={{ background: 'rgba(20,184,166,0.08)', border: '1px solid rgba(45,212,191,0.25)', borderRadius: 10, padding: 14, marginBottom: 24, fontSize: 12, color: '#99F6E4' }}>
          <strong style={{ color: '#5EEAD4' }}>Twilio webhook:</strong>{' '}
          <code style={{ wordBreak: 'break-all' }}>{status.inbound_webhook}</code>
          {status.transfer_number_masked && (
            <span style={{ display: 'block', marginTop: 8, color: 'rgba(153,246,228,0.8)' }}>
              Human transfer → {status.transfer_number_masked}
            </span>
          )}
        </div>
      )}

      {/* Simulator */}
      <div style={{ background: '#14141A', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: 18, marginBottom: 24 }}>
        <p style={{ fontSize: 11, fontWeight: 700, color: 'rgba(156,163,175,0.7)', textTransform: 'uppercase', letterSpacing: 0.8, margin: '0 0 10px' }}>Test without a phone call</p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            value={simSpeech}
            onChange={(e) => setSimSpeech(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runSim()}
            placeholder='Type what the caller would say…'
            style={{ flex: 1, minWidth: 200, padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.1)', background: '#0D0D12', color: '#F9FAFB', fontSize: 13 }}
          />
          <button type="button" onClick={runSim} disabled={simBusy} style={{ padding: '10px 16px', borderRadius: 8, border: 'none', background: accent, color: '#fff', fontWeight: 700, fontSize: 12, cursor: 'pointer', opacity: simBusy ? 0.6 : 1 }}>
            {simBusy ? '…' : simCallSid ? 'Next turn' : 'Start call'}
          </button>
          <button type="button" onClick={resetSim} style={{ padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.1)', background: 'transparent', color: '#9CA3AF', fontSize: 12, cursor: 'pointer' }}>
            Reset
          </button>
        </div>
        {simResult && (
          <p style={{ marginTop: 12, fontSize: 13, color: '#D1D5DB', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>{simResult}</p>
        )}
      </div>

      {/* Call log */}
      <p style={{ fontSize: 11, fontWeight: 700, color: 'rgba(156,163,175,0.6)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 10 }}>Recent calls</p>
      {loading ? (
        <p style={{ color: '#6B7280', fontSize: 13 }}>Loading…</p>
      ) : calls.length === 0 ? (
        <p style={{ color: '#6B7280', fontSize: 13 }}>No voice calls logged yet. Point Twilio at the inbound webhook or use the simulator above.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {calls.map((c) => (
            <div key={`${c.call_sid}-${c.started_at || c.completed_at}`} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: '#14141A', borderRadius: 10, border: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: 18 }}>📞</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: '#F3F4F6' }}>
                  {c.caller || 'Unknown'} · <span style={{ color: statusColor(c.status) }}>{c.status}</span>
                </p>
                <p style={{ margin: '2px 0 0', fontSize: 11, color: '#6B7280' }}>
                  {c.confirmation ? `Conf ${c.confirmation}` : c.error || c.call_sid}
                  {c.completed_at ? ` · ${new Date(c.completed_at).toLocaleString()}` : c.started_at ? ` · ${new Date(c.started_at).toLocaleString()}` : ''}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PrismVoiceCallCenter;
