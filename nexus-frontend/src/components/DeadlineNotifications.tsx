import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, X, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';

interface Deadline {
  id: string;
  name: string;
  value: string;
  date: Date;
  daysUntil: number;
  system?: string;
  rfpNumber?: string;
  status?: string;
}

interface DeadlineNotificationsProps {
  onNavigateToSystem?: (system: any) => void;
}

export const DeadlineNotifications: React.FC<DeadlineNotificationsProps> = ({ onNavigateToSystem }) => {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [isVisible, setIsVisible] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDeadline, setSelectedDeadline] = useState<Deadline | null>(null);

  const fetchDeadlines = useCallback(async () => {
    try {
      const response = await fetch((process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000') + '/gpss/opportunities');
      if (response.ok) {
        const data = await response.json();
        const opps = data.opportunities || [];
        const now = new Date();
        
        // Only show opportunities we're actually working on:
        // - Pipeline opportunities (isPipeline = true)
        // - OR presolicitations / sources sought / sole source by status
        const CALENDAR_STATUSES = [
          'active', 'pursuing', 'awaiting quotes', 'ready to bid', 'submitted',
          'submitted - awaiting award', 'in-progress', 'not started',
          'sources sought', 'sources sought submitted', 'presolicitation',
          'sole source', 'intent to sole source', 'no contact yet',
          'active - analyzing', 'solicitation', 'conditional',
        ];
        
        const relevantOpps = opps.filter((opp: any) => {
          // Must have a date
          if (!opp['Response Deadline'] && !opp['Deadline'] && !opp['dueDate'] && !opp['deadline']) return false;
          
          // Pipeline opportunities always show
          if (opp.isPipeline) return true;
          
          // Check status for presolicitation/sources sought/active work
          const status = (opp['Status'] || opp['internalStatus'] || opp['status'] || '').toLowerCase();
          return CALENDAR_STATUSES.some(s => status.includes(s));
        });

        const liveDeadlines: Deadline[] = relevantOpps
          .map((opp: any) => {
            const deadlineStr = opp['Response Deadline'] || opp['Deadline'] || opp['dueDate'] || opp['deadline'];
            const deadlineDate = new Date(deadlineStr);
            
            // Skip invalid dates
            if (isNaN(deadlineDate.getTime())) return null;
            
            const diffMs = deadlineDate.getTime() - now.getTime();
            const daysUntil = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
            
            // Format value
            const rawValue = opp['Estimated Value'] || opp['Value'] || opp['value'] || 0;
            const numValue = typeof rawValue === 'string' ? parseFloat(rawValue.replace(/[^0-9.]/g, '')) : rawValue;
            let valueStr = '';
            if (numValue >= 1000000) valueStr = `$${(numValue / 1000000).toFixed(1)}M`;
            else if (numValue >= 1000) valueStr = `$${(numValue / 1000).toFixed(0)}K`;
            else if (numValue > 0) valueStr = `$${numValue.toLocaleString()}`;
            
            return {
              id: opp.id || opp['RFP NUMBER'] || opp['rfpNumber'] || String(Math.random()),
              name: opp.Name || opp.Title || opp.title || 'Unnamed',
              value: valueStr,
              date: deadlineDate,
              daysUntil,
              system: 'GPSS',
              rfpNumber: opp['RFP NUMBER'] || opp['rfpNumber'] || '',
              status: opp['Status'] || opp['internalStatus'] || opp['status'] || '',
            };
          })
          .filter((d: Deadline | null): d is Deadline => d !== null && d.daysUntil >= -1 && d.daysUntil <= 90)
          .sort((a: Deadline, b: Deadline) => a.date.getTime() - b.date.getTime());
        
        if (liveDeadlines.length > 0) {
          setDeadlines(liveDeadlines);
          return;
        }
      }
    } catch (error) {
      console.error('Failed to fetch deadlines:', error);
    }
    
    // Fallback: empty — no fake data
    setDeadlines([]);
  }, []);

  useEffect(() => {
    fetchDeadlines();
    const interval = setInterval(fetchDeadlines, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchDeadlines]);

  if (!isVisible || deadlines.length === 0) return null;

  // Minimized view
  if (isMinimized) {
    const urgentCount = deadlines.filter(d => d.daysUntil <= 3).length;
    return (
      <div className="bg-gray-800/50 border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-6 py-1.5 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Calendar className="w-3 h-3" />
            <span>{deadlines.length} deadlines</span>
            {urgentCount > 0 && (
              <span className="text-red-400 font-medium">{urgentCount} this week</span>
            )}
          </div>
          <button
            onClick={() => setIsMinimized(false)}
            className="text-gray-500 hover:text-gray-300 text-xs"
          >
            Show Calendar
          </button>
        </div>
      </div>
    );
  }

  // Calendar view
  const monthStart = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const monthEnd = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
  const startDate = new Date(monthStart);
  startDate.setDate(startDate.getDate() - startDate.getDay()); // Start from Sunday

  const endDate = new Date(monthEnd);
  endDate.setDate(endDate.getDate() + (6 - endDate.getDay())); // End on Saturday

  const days = [];
  const currentDate = new Date(startDate);
  while (currentDate <= endDate) {
    days.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const getDeadlinesForDate = (date: Date) => {
    return deadlines.filter(d => {
      const deadlineDate = new Date(d.date);
      return deadlineDate.getDate() === date.getDate() &&
             deadlineDate.getMonth() === date.getMonth() &&
             deadlineDate.getFullYear() === date.getFullYear();
    });
  };

  const isToday = (date: Date) => {
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  };

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentMonth.getMonth();
  };

  return (
    <div className="bg-gray-800/50 border-b border-gray-700/50">
      <div className="max-w-7xl mx-auto px-6 py-3">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <Calendar className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-white">
              {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                className="p-1 text-gray-400 hover:text-white"
              >
                <ChevronLeft className="w-3 h-3" />
              </button>
              <button
                onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                className="p-1 text-gray-400 hover:text-white"
              >
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMinimized(true)}
              className="text-gray-500 hover:text-gray-300 text-xs px-2 py-1"
            >
              Minimize
            </button>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-500 hover:text-gray-300"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {/* Day headers */}
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-center text-xs text-gray-500 font-medium pb-1">
              {day}
            </div>
          ))}

          {/* Date cells */}
          {days.map((date, index) => {
            const dayDeadlines = getDeadlinesForDate(date);
            const hasDeadlines = dayDeadlines.length > 0;
            const isCurrentDay = isToday(date);
            const inMonth = isCurrentMonth(date);

            return (
              <div
                key={index}
                className={`
                  min-h-[60px] p-1 rounded border text-xs
                  ${isCurrentDay ? 'bg-blue-500/20 border-blue-500/50' : 'bg-gray-800/50 border-gray-700/50'}
                  ${!inMonth ? 'opacity-30' : ''}
                  ${hasDeadlines ? 'border-yellow-500/30' : ''}
                `}
              >
                {/* Date number */}
                <div className={`text-xs font-medium mb-1 ${isCurrentDay ? 'text-blue-400' : inMonth ? 'text-gray-300' : 'text-gray-600'}`}>
                  {date.getDate()}
                </div>

                {/* Deadlines */}
                {hasDeadlines && (
                  <div className="space-y-0.5">
                    {dayDeadlines.slice(0, 2).map(deadline => (
                      <div
                        key={deadline.id}
                        className={`rounded px-1 py-0.5 text-[10px] truncate cursor-pointer transition-all ${
                          deadline.daysUntil <= 2
                            ? 'bg-red-500/20 border border-red-500/30 hover:bg-red-500/40'
                            : deadline.daysUntil <= 7
                            ? 'bg-yellow-500/20 border border-yellow-500/30 hover:bg-yellow-500/40'
                            : 'bg-blue-500/20 border border-blue-500/30 hover:bg-blue-500/40'
                        }`}
                        title={`${deadline.name} - ${deadline.value}\nClick to view details`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDeadline(deadline);
                        }}
                      >
                        <div className="font-medium text-white truncate">{deadline.name}</div>
                        {deadline.value && <div className="text-green-400">{deadline.value}</div>}
                      </div>
                    ))}
                    {dayDeadlines.length > 2 && (
                      <div
                        className="text-[10px] text-gray-400 text-center cursor-pointer hover:text-white"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDeadline(dayDeadlines[2]);
                        }}
                      >
                        +{dayDeadlines.length - 2} more
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-blue-500/20 border border-blue-500/50"></div>
            <span>Today</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500/20 border border-red-500/30"></div>
            <span>Due in 1-2 days</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-yellow-500/20 border border-yellow-500/30"></div>
            <span>Due this week</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-blue-500/20 border border-blue-500/30"></div>
            <span>Upcoming</span>
          </div>
          <div className="ml-auto text-gray-500">
            {deadlines.length} deadline{deadlines.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Deadline Detail Popup */}
        {selectedDeadline && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedDeadline(null)}>
            <div className="bg-gray-800 border border-gray-600 rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedDeadline.name}</h3>
                  {selectedDeadline.rfpNumber && (
                    <p className="text-sm text-gray-400 mt-1">{selectedDeadline.rfpNumber}</p>
                  )}
                </div>
                <button onClick={() => setSelectedDeadline(null)} className="text-gray-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between bg-gray-700/50 rounded p-3">
                  <span className="text-sm text-gray-400">Deadline</span>
                  <span className={`text-sm font-bold ${
                    selectedDeadline.daysUntil <= 2 ? 'text-red-400' : selectedDeadline.daysUntil <= 7 ? 'text-yellow-400' : 'text-blue-400'
                  }`}>
                    {selectedDeadline.date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                    {selectedDeadline.daysUntil >= 0 ? ` (${selectedDeadline.daysUntil} day${selectedDeadline.daysUntil !== 1 ? 's' : ''})` : ' (PAST DUE)'}
                  </span>
                </div>

                {selectedDeadline.value && (
                  <div className="flex items-center justify-between bg-gray-700/50 rounded p-3">
                    <span className="text-sm text-gray-400">Estimated Value</span>
                    <span className="text-sm font-bold text-green-400">{selectedDeadline.value}</span>
                  </div>
                )}

                {selectedDeadline.status && (
                  <div className="flex items-center justify-between bg-gray-700/50 rounded p-3">
                    <span className="text-sm text-gray-400">Status</span>
                    <span className="text-sm font-semibold text-white">{selectedDeadline.status}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    const targetSystem = selectedDeadline.system === 'ATLAS PM' ? 'atlas' : 'gpss';
                    setSelectedDeadline(null);
                    // Use setTimeout to ensure state update completes before navigation
                    setTimeout(() => {
                      if (onNavigateToSystem) {
                        onNavigateToSystem(targetSystem);
                      }
                    }, 50);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 px-4 rounded-lg transition"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Opportunity →
                </button>
                <button
                  onClick={() => setSelectedDeadline(null)}
                  className="px-4 py-2.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
