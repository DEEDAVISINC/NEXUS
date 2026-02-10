import React, { useState, useEffect } from 'react';
import { Calendar, X, ChevronLeft, ChevronRight } from 'lucide-react';

interface Deadline {
  id: string;
  name: string;
  value: string;
  date: Date;
  daysUntil: number;
}

export const DeadlineNotifications: React.FC = () => {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [isVisible, setIsVisible] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  useEffect(() => {
    // Hardcoded deadlines
    setDeadlines([
      { id: '1', name: 'Henry Ford Cabinets', value: '$15K', date: new Date(2026, 1, 11), daysUntil: 2 },
      { id: '2', name: 'Oakland Salt', value: '$50K', date: new Date(2026, 1, 12), daysUntil: 3 },
      { id: '3', name: 'Flow Meters', value: '$8K', date: new Date(2026, 1, 12), daysUntil: 3 },
      { id: '4', name: 'CPS Padlocks', value: '$32K', date: new Date(2026, 1, 13), daysUntil: 4 },
      { id: '5', name: 'Auburn Pressure Washing', value: '$5K', date: new Date(2026, 1, 13), daysUntil: 4 },
      { id: '6', name: 'Exam Stools', value: '$3K', date: new Date(2026, 1, 16), daysUntil: 7 },
      { id: '7', name: 'Truck Equipment', value: '$20K', date: new Date(2026, 1, 17), daysUntil: 8 },
      { id: '8', name: 'Livonia Materials', value: '$15K', date: new Date(2026, 1, 23), daysUntil: 14 }
    ]);
  }, []);

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
                        className="bg-red-500/20 border border-red-500/30 rounded px-1 py-0.5 text-[10px] truncate hover:bg-red-500/30 cursor-pointer"
                        title={`${deadline.name} - ${deadline.value}`}
                      >
                        <div className="font-medium text-white truncate">{deadline.name}</div>
                        <div className="text-green-400">{deadline.value}</div>
                      </div>
                    ))}
                    {dayDeadlines.length > 2 && (
                      <div className="text-[10px] text-gray-500 text-center">
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
            <span>Bid Deadline</span>
          </div>
          <div className="ml-auto text-gray-500">
            {deadlines.length} total deadlines this month
          </div>
        </div>
      </div>
    </div>
  );
};
