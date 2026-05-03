import React, { useState, useEffect, useCallback } from 'react';

const API = (window as any).__NEXUS_API__ || '';

interface CalendarEvent {
  id: string;
  title: string;
  start_iso: string;
  end_iso: string;
  display_dt: string;
  location: string;
  description: string;
  system: string;
  event_type: string;
  internal_id: string;
  party_name: string;
  party_email: string;
  party_phone: string;
  status: string;
  ics_filename: string;
}

const SYSTEM_COLORS: Record<string, string> = {
  PRISM: '#1e40af', NEMT: '#7c3aed', SHIELD: '#f5c23e', GPSS: '#059669',
  COMPASS: '#0891b2', ATLAS: '#ea580c', VERTEX: '#dc2626', GBIS: '#16a34a',
  DDCSS: '#6b7280', LBPC: '#0284c7', JETA: '#9333ea', NEXUS: '#374151',
  DEADLINE: '#ef4444',
};

const SYSTEM_EMOJIS: Record<string, string> = {
  PRISM: '🔬', NEMT: '🚗', SHIELD: '🛡️', GPSS: '🏛️', COMPASS: '🧭',
  ATLAS: '📐', VERTEX: '💰', GBIS: '🎯', DDCSS: '🏢', LBPC: '📋',
  JETA: '✈️', NEXUS: '📅', DEADLINE: '🔥',
};

const ALL_SYSTEMS = Object.keys(SYSTEM_COLORS);

interface AddEventForm {
  title: string;
  start_date: string;
  start_time: string;
  end_time: string;
  location: string;
  description: string;
  system: string;
  event_type: string;
  party_name: string;
  party_email: string;
  party_phone: string;
  send_confirmation: boolean;
  confirmation_what: string;
  confirmation_why: string;
  confirmation_bring: string;
}

const EMPTY_FORM: AddEventForm = {
  title: '', start_date: '', start_time: '12:00', end_time: '13:00',
  location: '', description: '', system: 'NEXUS', event_type: 'meeting',
  party_name: '', party_email: '', party_phone: '',
  send_confirmation: false, confirmation_what: '', confirmation_why: '',
  confirmation_bring: '',
};

export default function NexusCalendarSystem({ onBackToNexus }: { onBackToNexus: () => void }) {
  const [events, setEvents]           = useState<CalendarEvent[]>([]);
  const [loading, setLoading]         = useState(true);
  const [filterSystem, setFilterSystem] = useState('');
  const [view, setView]               = useState<'list' | 'month'>('list');
  const [showAdd, setShowAdd]         = useState(false);
  const [form, setForm]               = useState<AddEventForm>(EMPTY_FORM);
  const [saving, setSaving]           = useState(false);
  const [saveMsg, setSaveMsg]         = useState('');
  const [selected, setSelected]       = useState<CalendarEvent | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const qs = filterSystem ? `?system=${filterSystem}` : '';
      const r  = await fetch(`${API}/nexus/calendar/events${qs}`);
      const d  = await r.json();
      setEvents(d.events || []);
    } catch { setEvents([]); }
    setLoading(false);
  }, [filterSystem]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async () => {
    if (!form.title || !form.start_date) {
      setSaveMsg('Title and date are required.'); return;
    }
    setSaving(true); setSaveMsg('');
    try {
      const start_iso = `${form.start_date}T${form.start_time}:00`;
      const end_iso   = `${form.start_date}T${form.end_time}:00`;
      const body = {
        title: form.title, start_iso, end_iso,
        location: form.location, description: form.description,
        system: form.system, event_type: form.event_type,
        party_name: form.party_name, party_email: form.party_email,
        party_phone: form.party_phone,
        send_confirmation: form.send_confirmation,
        confirmation_what: form.confirmation_what,
        confirmation_why: form.confirmation_why,
        confirmation_bring: form.confirmation_bring,
      };
      const r = await fetch(`${API}/nexus/calendar/events`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const d = await r.json();
      if (d.success) {
        setSaveMsg('✅ Event added to calendar.');
        setForm(EMPTY_FORM);
        setShowAdd(false);
        load();
      } else {
        setSaveMsg(`❌ ${d.error || 'Failed to save.'}`);
      }
    } catch { setSaveMsg('❌ Server error.'); }
    setSaving(false);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Remove this event from the calendar?')) return;
    await fetch(`${API}/nexus/calendar/events/${id}`, { method: 'DELETE' });
    setSelected(null);
    load();
  };

  // ── Group events by date for list view ──
  const grouped: Record<string, CalendarEvent[]> = {};
  events.forEach(e => {
    const d = e.start_iso?.slice(0, 10) || 'unknown';
    if (!grouped[d]) grouped[d] = [];
    grouped[d].push(e);
  });
  const sortedDates = Object.keys(grouped).sort();

  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="min-h-screen bg-[#050f2e] text-white">
      {/* ── Header ── */}
      <div className="bg-[#081849] border-b border-[#1c2f6a] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={onBackToNexus} className="text-[#8ea2d6] hover:text-white text-sm">← NEXUS</button>
          <div>
            <h1 className="text-xl font-black text-white">📅 NEXUS Calendar</h1>
            <p className="text-xs text-[#8ea2d6]">All systems · All events · One view</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Subscribe feed link */}
          <a
            href={`${API}/nexus/calendar/feed.ics`}
            target="_blank" rel="noopener noreferrer"
            className="text-xs bg-[#1c2f6a] hover:bg-[#2a3f8a] text-[#8ea2d6] hover:text-white px-3 py-2 rounded-lg transition"
            title="Subscribe in Apple/Google/Outlook Calendar"
          >
            📲 Subscribe
          </a>
          <button
            onClick={() => { setShowAdd(true); setSaveMsg(''); }}
            className="bg-[#f5c23e] hover:bg-[#fcd75a] text-[#081849] px-4 py-2 rounded-lg text-sm font-bold transition"
          >
            + Add Event
          </button>
        </div>
      </div>

      {/* ── Filter bar ── */}
      <div className="px-6 py-3 bg-[#060e24] border-b border-[#1c2f6a] flex items-center gap-3 flex-wrap">
        <span className="text-xs text-[#8ea2d6] font-bold uppercase tracking-wider">Filter:</span>
        <button
          onClick={() => setFilterSystem('')}
          className={`text-xs px-3 py-1 rounded-full border transition ${!filterSystem ? 'bg-white/10 border-white/30 text-white' : 'border-[#1c2f6a] text-[#8ea2d6] hover:text-white'}`}
        >All Systems</button>
        {ALL_SYSTEMS.map(s => (
          <button
            key={s}
            onClick={() => setFilterSystem(s === filterSystem ? '' : s)}
            className={`text-xs px-3 py-1 rounded-full border transition ${filterSystem === s ? 'text-white' : 'border-[#1c2f6a] text-[#8ea2d6] hover:text-white'}`}
            style={filterSystem === s ? { background: SYSTEM_COLORS[s] + '33', borderColor: SYSTEM_COLORS[s] } : {}}
          >
            {SYSTEM_EMOJIS[s]} {s}
          </button>
        ))}
      </div>

      <div className="flex h-[calc(100vh-130px)]">
        {/* ── Event list ── */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="text-[#8ea2d6] text-sm animate-pulse">Loading calendar…</div>
          ) : sortedDates.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-4xl mb-3">📅</div>
              <p className="text-[#8ea2d6] text-sm">No events yet. Click <strong>+ Add Event</strong> to get started.</p>
            </div>
          ) : (
            sortedDates.map(date => {
              const isToday   = date === today;
              const isPast    = date < today;
              const dateLabel = new Date(date + 'T12:00:00').toLocaleDateString('en-US', {
                weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
              });
              return (
                <div key={date} className="mb-6">
                  <div className={`flex items-center gap-2 mb-2 ${isPast ? 'opacity-50' : ''}`}>
                    <div className={`text-xs font-bold uppercase tracking-wider ${isToday ? 'text-[#f5c23e]' : 'text-[#8ea2d6]'}`}>
                      {isToday ? '🔴 TODAY — ' : ''}{dateLabel}
                    </div>
                    <div className="flex-1 h-px bg-[#1c2f6a]" />
                  </div>
                  <div className="space-y-2">
                    {grouped[date].map(e => {
                      const color  = SYSTEM_COLORS[e.system] || '#374151';
                      const emoji  = SYSTEM_EMOJIS[e.system] || '📅';
                      const time   = e.start_iso?.slice(11, 16) || '';
                      const isSelected = selected?.id === e.id;
                      return (
                        <div
                          key={e.id}
                          onClick={() => setSelected(isSelected ? null : e)}
                          className={`rounded-xl border cursor-pointer transition ${isSelected ? 'bg-[#0d1f52]' : 'bg-[#081235] hover:bg-[#0d1a3f]'}`}
                          style={{ borderColor: isSelected ? color : '#1c2f6a' }}
                        >
                          <div className="flex items-center gap-3 px-4 py-3">
                            <div className="w-1 h-10 rounded-full flex-shrink-0" style={{ background: color }} />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-bold text-white truncate">{e.title}</span>
                                <span className="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0"
                                  style={{ background: color + '22', color }}>
                                  {emoji} {e.system}
                                </span>
                              </div>
                              <div className="flex items-center gap-3 mt-0.5 text-xs text-[#8ea2d6]">
                                {time && <span>🕐 {time}</span>}
                                {e.location && <span>📍 {e.location}</span>}
                                {e.party_name && <span>👤 {e.party_name}</span>}
                              </div>
                            </div>
                            <div className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${
                              e.status === 'scheduled' ? 'bg-blue-500/20 text-blue-400'
                              : e.status === 'confirmed' ? 'bg-green-500/20 text-green-400'
                              : 'bg-gray-500/20 text-gray-400'
                            }`}>{e.status}</div>
                          </div>

                          {/* Expanded detail */}
                          {isSelected && (
                            <div className="px-4 pb-4 border-t border-[#1c2f6a] pt-3 space-y-2">
                              {e.description && (
                                <p className="text-xs text-[#8ea2d6]">{e.description}</p>
                              )}
                              <div className="flex flex-wrap gap-3 text-xs text-[#8ea2d6]">
                                {e.party_email && <span>✉️ {e.party_email}</span>}
                                {e.party_phone && <span>📱 {e.party_phone}</span>}
                                {e.internal_id && <span>🔖 Ref: {e.internal_id}</span>}
                              </div>
                              <div className="flex gap-2 pt-1">
                                {e.ics_filename && (
                                  <a
                                    href={`${API}/static/calendars/${e.ics_filename}`}
                                    download
                                    className="text-xs bg-[#1e40af]/30 hover:bg-[#1e40af]/50 text-blue-300 px-3 py-1.5 rounded-lg transition"
                                    onClick={ev => ev.stopPropagation()}
                                  >📥 Download .ics</a>
                                )}
                                <button
                                  onClick={ev => { ev.stopPropagation(); handleDelete(e.id); }}
                                  className="text-xs bg-red-500/20 hover:bg-red-500/40 text-red-400 px-3 py-1.5 rounded-lg transition"
                                >🗑 Remove</button>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Add Event Modal ── */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#081849] border border-[#1c2f6a] rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-[#1c2f6a] flex justify-between items-center">
              <h2 className="text-lg font-black text-white">📅 Add Calendar Event</h2>
              <button onClick={() => setShowAdd(false)} className="text-[#8ea2d6] hover:text-white text-xl">×</button>
            </div>
            <div className="px-6 py-4 space-y-4">
              {/* Title */}
              <div>
                <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Title *</label>
                <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="e.g. CO Meeting — USACE W912DR"
                  className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
              </div>

              {/* Date + Times */}
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-1">
                  <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Date *</label>
                  <input type="date" value={form.start_date} onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))}
                    className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white focus:border-[#f5c23e] focus:outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Start</label>
                  <input type="time" value={form.start_time} onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))}
                    className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white focus:border-[#f5c23e] focus:outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">End</label>
                  <input type="time" value={form.end_time} onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))}
                    className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white focus:border-[#f5c23e] focus:outline-none" />
                </div>
              </div>

              {/* System + Type */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">System</label>
                  <select value={form.system} onChange={e => setForm(f => ({ ...f, system: e.target.value }))}
                    className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white focus:border-[#f5c23e] focus:outline-none">
                    {ALL_SYSTEMS.map(s => <option key={s} value={s}>{SYSTEM_EMOJIS[s]} {s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Type</label>
                  <select value={form.event_type} onChange={e => setForm(f => ({ ...f, event_type: e.target.value }))}
                    className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white focus:border-[#f5c23e] focus:outline-none">
                    {['meeting', 'appointment', 'signing', 'deadline', 'call', 'ride'].map(t =>
                      <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>

              {/* Location */}
              <div>
                <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Location / Link</label>
                <input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                  placeholder="Address or Zoom link"
                  className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-xs font-bold text-[#8ea2d6] uppercase tracking-wider mb-1">Notes</label>
                <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  rows={2} placeholder="Any additional context…"
                  className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none resize-none" />
              </div>

              {/* Other party */}
              <div className="border border-[#1c2f6a] rounded-xl p-4 space-y-3">
                <p className="text-xs font-bold text-[#8ea2d6] uppercase tracking-wider">Other Party (optional)</p>
                <div className="grid grid-cols-2 gap-3">
                  <input value={form.party_name} onChange={e => setForm(f => ({ ...f, party_name: e.target.value }))}
                    placeholder="Name"
                    className="bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
                  <input value={form.party_phone} onChange={e => setForm(f => ({ ...f, party_phone: e.target.value }))}
                    placeholder="Phone"
                    className="bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
                </div>
                <input value={form.party_email} onChange={e => setForm(f => ({ ...f, party_email: e.target.value }))}
                  placeholder="Email"
                  className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />

                {/* Confirmation toggle */}
                {(form.party_email || form.party_phone) && (
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.send_confirmation}
                      onChange={e => setForm(f => ({ ...f, send_confirmation: e.target.checked }))}
                      className="accent-[#f5c23e]" />
                    <span className="text-xs text-[#8ea2d6]">Send confirmation email + text to other party</span>
                  </label>
                )}

                {form.send_confirmation && (
                  <div className="space-y-2 pt-1">
                    <input value={form.confirmation_what} onChange={e => setForm(f => ({ ...f, confirmation_what: e.target.value }))}
                      placeholder="WHAT — e.g. Capability review call — drug testing"
                      className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
                    <input value={form.confirmation_why} onChange={e => setForm(f => ({ ...f, confirmation_why: e.target.value }))}
                      placeholder="WHY — e.g. Follow-up to solicitation W912DR25QA005"
                      className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
                    <input value={form.confirmation_bring} onChange={e => setForm(f => ({ ...f, confirmation_bring: e.target.value }))}
                      placeholder="BRING — e.g. Capability statement, references"
                      className="w-full bg-[#050f2e] border border-[#1c2f6a] rounded-lg px-3 py-2 text-sm text-white placeholder:text-[#6b7ba6] focus:border-[#f5c23e] focus:outline-none" />
                  </div>
                )}
              </div>

              {saveMsg && (
                <p className={`text-xs ${saveMsg.startsWith('✅') ? 'text-green-400' : 'text-red-400'}`}>{saveMsg}</p>
              )}

              <button onClick={handleSave} disabled={saving}
                className="w-full bg-[#f5c23e] hover:bg-[#fcd75a] disabled:opacity-60 text-[#081849] py-3 rounded-xl text-sm font-black transition">
                {saving ? 'Saving…' : '📅 Add to Calendar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
