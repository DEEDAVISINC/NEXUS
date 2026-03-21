import React, { useState, useEffect, useCallback } from 'react';
import { Send, Clock, FileText, ChevronDown, ChevronRight, Folder, Copy, Check, X, Mail, CheckCircle, Circle, Flame, ArrowUp, Calendar } from 'lucide-react';

interface AgendaItem {
  id: string;
  name: string;
  stage: string;
  action: string;
  folder: string;
  lastModified: string;
  daysAgo: number;
  to: string;
  cc: string;
  subject: string;
  hasEmail: boolean;
  hasWorkflow: boolean;
  capStatements: string[];
  buyerDocCount: number;
  supplierDocCount: number;
  checklist: string[];
  priority?: string;
  status?: string;
  dueDate?: string;
  project?: string;
  recordId?: string;
  type?: string;
}

interface AgendaSection {
  id: string;
  title: string;
  subtitle: string;
  color: string;
  items: AgendaItem[];
  type?: string;
}

interface AgendaData {
  date: string;
  sections: AgendaSection[];
  stats: {
    total_tasks: number;
    completed: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    ready_to_send: number;
    supplier_pending: number;
  };
}

interface BidDetail {
  id: string;
  name: string;
  email: {
    to?: string;
    cc?: string;
    subject?: string;
    body?: string;
    checklist?: string[];
    raw?: string;
  };
  buyerDocs: { name: string; type: string; path: string }[];
}

const SECTION_CONFIG: Record<string, { icon: React.ReactNode; accent: string; bg: string }> = {
  critical: { icon: <Flame className="w-5 h-5" />, accent: 'text-red-400', bg: 'bg-red-500' },
  high: { icon: <ArrowUp className="w-5 h-5" />, accent: 'text-orange-400', bg: 'bg-orange-500' },
  ready_to_send: { icon: <Send className="w-5 h-5" />, accent: 'text-emerald-400', bg: 'bg-emerald-500' },
  medium: { icon: <Calendar className="w-5 h-5" />, accent: 'text-sky-400', bg: 'bg-sky-500' },
  supplier_pending: { icon: <Clock className="w-5 h-5" />, accent: 'text-amber-400', bg: 'bg-amber-500' },
  low: { icon: <FileText className="w-5 h-5" />, accent: 'text-gray-400', bg: 'bg-gray-600' },
  done: { icon: <CheckCircle className="w-5 h-5" />, accent: 'text-emerald-400', bg: 'bg-emerald-600' },
};

export const AgendaDashboard: React.FC = () => {
  const [data, setData] = useState<AgendaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedBid, setExpandedBid] = useState<string | null>(null);
  const [bidDetail, setBidDetail] = useState<BidDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [completingTask, setCompletingTask] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    critical: true,
    high: true,
    ready_to_send: false,
    medium: false,
    supplier_pending: false,
    low: false,
    done: false,
  });

  const fetchAgenda = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/agenda?view=today');
      if (res.ok) setData(await res.json());
    } catch (err) {
      console.error('Agenda fetch failed:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgenda();
    const iv = setInterval(fetchAgenda, 5 * 60 * 1000);
    return () => clearInterval(iv);
  }, [fetchAgenda]);

  const openBid = async (item: AgendaItem) => {
    if (item.type === 'task') return;
    if (expandedBid === item.id) {
      setExpandedBid(null);
      setBidDetail(null);
      return;
    }
    setExpandedBid(item.id);
    setBidDetail(null);

    if (item.hasEmail) {
      setDetailLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/agenda/bid/${item.id}`);
        if (res.ok) setBidDetail(await res.json());
      } catch (err) {
        console.error('Bid detail fetch failed:', err);
      } finally {
        setDetailLoading(false);
      }
    }
  };

  const markDone = async (item: AgendaItem) => {
    if (!item.recordId) return;
    setCompletingTask(item.recordId);
    try {
      const res = await fetch(`http://localhost:8000/api/agenda/task/${item.recordId}/done`, { method: 'POST' });
      if (res.ok) {
        setData(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            sections: prev.sections.map(s => ({
              ...s,
              items: s.items.filter(i => i.recordId !== item.recordId),
            })),
          };
        });
      }
    } catch (err) {
      console.error('Mark done failed:', err);
    } finally {
      setCompletingTask(null);
    }
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      console.error('Copy failed');
    }
  };

  if (loading) {
    return <div className="text-center py-16 text-gray-400">Loading workbench...</div>;
  }

  if (!data) {
    return <div className="text-center py-16 text-gray-400">Could not load. Is the API running on port 8000?</div>;
  }

  const { stats } = data;
  const totalActive = stats.critical + stats.high + stats.medium + stats.low;

  return (
    <div className="space-y-5">
      {/* Stats bar */}
      <div className="flex items-center gap-6 px-1 flex-wrap">
        {stats.critical > 0 && <Stat value={stats.critical} label="Critical" color="red" />}
        <Stat value={stats.high} label="High" color="orange" />
        <Stat value={stats.ready_to_send} label="Emails" color="emerald" />
        <Stat value={stats.medium} label="This Week" color="sky" />
        <Stat value={stats.low} label="Backlog" color="gray" />
        <div className="ml-auto flex items-center gap-4">
          {stats.completed > 0 && <span className="text-xs text-emerald-500">{stats.completed} completed</span>}
          <span className="text-sm text-gray-500">{totalActive} active</span>
        </div>
      </div>

      {/* Sections */}
      {data.sections.map(section => {
        if (!section.items.length) return null;
        const cfg = SECTION_CONFIG[section.id] || SECTION_CONFIG.medium;
        const isOpen = expandedSections[section.id] ?? false;
        const isTaskSection = section.type === 'tasks';

        return (
          <div key={section.id} className="bg-gray-800/80 border border-gray-700/60 rounded-xl overflow-hidden">
            <button
              onClick={() => setExpandedSections(p => ({ ...p, [section.id]: !p[section.id] }))}
              className="w-full flex items-center gap-3 px-5 py-3.5 hover:bg-gray-700/30 transition"
            >
              <span className={cfg.accent}>{cfg.icon}</span>
              <span className="font-semibold text-white">{section.title}</span>
              <span className={`${cfg.bg} text-white text-xs font-bold px-2 py-0.5 rounded-full`}>
                {section.items.length}
              </span>
              <span className="text-sm text-gray-500 ml-2 hidden sm:inline">{section.subtitle}</span>
              <span className="ml-auto text-gray-500">
                {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </span>
            </button>

            {isOpen && (
              <div className="border-t border-gray-700/40">
                {section.items.map((item) => (
                  <div key={item.id || item.recordId}>
                    {isTaskSection ? (
                      <TaskRow item={item} onDone={markDone} completing={completingTask} isDone={section.id === 'done'} />
                    ) : (
                      <>
                        <BidRow item={item} expandedBid={expandedBid} onOpen={openBid} />
                        {expandedBid === item.id && (
                          <div className="bg-gray-900/50 border-b border-gray-700/30 px-5 py-4">
                            {detailLoading ? (
                              <div className="text-sm text-gray-400 py-4">Loading email...</div>
                            ) : bidDetail?.email ? (
                              <BidDetailView
                                detail={bidDetail}
                                item={item}
                                onCopy={copyToClipboard}
                                copied={copied}
                                onClose={() => { setExpandedBid(null); setBidDetail(null); }}
                              />
                            ) : (
                              <div className="text-sm text-gray-400">
                                <p className="mb-2 font-medium text-white">{item.name}</p>
                                <p>{item.action}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

const PROJECT_COLORS: Record<string, string> = {
  'Drug Testing': 'bg-red-500/15 text-red-400',
  'DNA Testing': 'bg-purple-500/15 text-purple-400',
  'Fingerprinting': 'bg-green-400/15 text-green-400',
  'Registrations': 'bg-cyan-500/15 text-cyan-400',
  'NEMT': 'bg-teal-500/15 text-teal-400',
  'Outreach': 'bg-amber-500/15 text-amber-400',
  'Courier': 'bg-indigo-500/15 text-indigo-400',
  'Notary': 'bg-pink-500/15 text-pink-400',
  'Certifications': 'bg-emerald-500/15 text-emerald-400',
  'ATF/NFA Lane': 'bg-orange-500/15 text-orange-400',
  'Interstate Licensure': 'bg-sky-500/15 text-sky-400',
  'Business Dev': 'bg-violet-500/15 text-violet-400',
};

const ActionDetail: React.FC<{ action: string }> = ({ action }) => {
  const parts = action.split('|').map(p => p.trim()).filter(Boolean);
  const toLine = parts.find(p => p.startsWith('TO:'));
  const urlLine = parts.find(p => p.startsWith('URL:'));
  const phoneLine = parts.find(p => p.startsWith('Phone:'));
  const otherParts = parts.filter(p => !p.startsWith('TO:') && !p.startsWith('URL:') && !p.startsWith('Phone:'));

  return (
    <div className="text-xs mt-1 space-y-0.5">
      {toLine && (
        <div className="text-emerald-400/80 font-mono">{toLine}</div>
      )}
      {urlLine && (
        <div className="text-sky-400/80 font-mono">{urlLine}</div>
      )}
      {phoneLine && (
        <div className="text-amber-400/80 font-mono">{phoneLine}</div>
      )}
      {otherParts.length > 0 && (
        <div className="text-gray-400">{otherParts.join(' · ')}</div>
      )}
    </div>
  );
};

const TaskRow: React.FC<{
  item: AgendaItem;
  onDone: (item: AgendaItem) => void;
  completing: string | null;
  isDone?: boolean;
}> = ({ item, onDone, completing, isDone }) => {
  const isCompleting = completing === item.recordId;
  const pColor = item.project ? (PROJECT_COLORS[item.project] || 'bg-gray-700/50 text-gray-400') : '';

  return (
    <div className={`flex items-start gap-3 px-5 py-3 border-b border-gray-700/30 hover:bg-gray-700/20 transition group ${isDone ? 'opacity-60' : ''}`}>
      {!isDone ? (
        <button
          onClick={() => onDone(item)}
          disabled={isCompleting}
          className="mt-0.5 flex-shrink-0 text-gray-600 hover:text-emerald-400 transition"
          title="Mark done"
        >
          {isCompleting ? (
            <CheckCircle className="w-5 h-5 text-emerald-400 animate-pulse" />
          ) : (
            <Circle className="w-5 h-5 group-hover:text-emerald-400" />
          )}
        </button>
      ) : (
        <CheckCircle className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`font-medium text-sm ${isDone ? 'text-gray-400 line-through' : 'text-white'}`}>{item.name}</span>
          {item.project && (
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${pColor}`}>
              {item.project}
            </span>
          )}
          {item.status === 'BLOCKED' && (
            <span className="text-[10px] bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded font-medium">Blocked</span>
          )}
        </div>
        {item.action && <ActionDetail action={item.action} />}
      </div>
      {item.dueDate && (
        <span className="text-xs text-gray-600 flex-shrink-0 mt-0.5">{item.dueDate}</span>
      )}
    </div>
  );
};

const BidRow: React.FC<{
  item: AgendaItem;
  expandedBid: string | null;
  onOpen: (item: AgendaItem) => void;
}> = ({ item, expandedBid, onOpen }) => (
  <button
    onClick={() => onOpen(item)}
    className={`w-full text-left px-5 py-3 flex items-start gap-4 hover:bg-gray-700/20 transition border-b border-gray-700/30 ${
      expandedBid === item.id ? 'bg-gray-700/30' : ''
    }`}
  >
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-3">
        <span className="font-medium text-white text-sm">{item.name}</span>
        {item.daysAgo <= 2 && (
          <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded font-medium">Recent</span>
        )}
      </div>
      {item.to ? (
        <div className="text-xs text-gray-400 mt-1 truncate">
          <span className="text-gray-500">To:</span> {item.to}
          {item.subject && <span className="ml-3 text-gray-500">Subj:</span>}
          {item.subject && <span> {item.subject.slice(0, 50)}{item.subject.length > 50 ? '...' : ''}</span>}
        </div>
      ) : (
        <div className="text-xs text-gray-400 mt-1">{item.action}</div>
      )}
    </div>
    <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
      {item.capStatements.length > 0 && (
        <span className="text-[10px] bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded">Cap Statement</span>
      )}
      {item.hasEmail && (
        <span className="text-[10px] bg-emerald-500/15 text-emerald-400 px-1.5 py-0.5 rounded">Email Ready</span>
      )}
      <span className="text-xs text-gray-600">{item.lastModified}</span>
    </div>
  </button>
);

const Stat: React.FC<{ value: number; label: string; color: string }> = ({ value, label, color }) => {
  const colors: Record<string, string> = {
    red: 'text-red-400',
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    sky: 'text-sky-400',
    orange: 'text-orange-400',
    gray: 'text-gray-400',
  };
  return (
    <div className="flex items-baseline gap-2">
      <span className={`text-2xl font-bold ${colors[color] || 'text-white'}`}>{value}</span>
      <span className="text-xs text-gray-500">{label}</span>
    </div>
  );
};

const BidDetailView: React.FC<{
  detail: BidDetail;
  item: AgendaItem;
  onCopy: (text: string, label: string) => void;
  copied: string | null;
  onClose: () => void;
}> = ({ detail, item, onCopy, copied, onClose }) => {
  const email = detail.email;
  const to = email.to || item.to;
  const subject = email.subject || item.subject;
  const body = email.body || '';

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-white text-sm">{item.name}</span>
          </div>
          {to && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-10">To:</span>
              <span className="text-sm text-white font-mono">{to}</span>
              <button onClick={() => onCopy(to, 'to')} className="text-gray-500 hover:text-white transition p-0.5" title="Copy email address">
                {copied === 'to' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              </button>
            </div>
          )}
          {email.cc && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-10">CC:</span>
              <span className="text-sm text-gray-300 font-mono">{email.cc}</span>
            </div>
          )}
          {subject && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-10">Subj:</span>
              <span className="text-sm text-gray-200">{subject}</span>
              <button onClick={() => onCopy(subject, 'subject')} className="text-gray-500 hover:text-white transition p-0.5" title="Copy subject">
                {copied === 'subject' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              </button>
            </div>
          )}
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white p-1">
          <X className="w-4 h-4" />
        </button>
      </div>

      {body && (
        <div className="relative">
          <div className="bg-gray-800 border border-gray-700/60 rounded-lg p-4 text-sm text-gray-200 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto font-[system-ui]">
            {body}
          </div>
          <button
            onClick={() => onCopy(body, 'body')}
            className={`absolute top-2 right-2 flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition ${
              copied === 'body' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
            }`}
          >
            {copied === 'body' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
            {copied === 'body' ? 'Copied' : 'Copy Email'}
          </button>
        </div>
      )}

      {detail.buyerDocs.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wider">Attachments</div>
          <div className="flex flex-wrap gap-2">
            {detail.buyerDocs.map((doc, i) => (
              <div key={i} className="flex items-center gap-1.5 bg-gray-800 border border-gray-700/50 rounded px-2.5 py-1.5 text-xs text-gray-300">
                <Folder className="w-3 h-3 text-gray-500" />
                <span className="truncate max-w-[280px]">{doc.name}</span>
                <span className="text-gray-600 uppercase">{doc.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {item.checklist.length > 0 && (
        <div>
          <div className="text-xs text-gray-500 mb-1.5 font-medium uppercase tracking-wider">Before Sending</div>
          <div className="space-y-1">
            {item.checklist.map((step, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-gray-400">
                <span className="text-gray-600 mt-0.5">{'>'}</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgendaDashboard;
