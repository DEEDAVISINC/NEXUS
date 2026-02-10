import React, { useState, useEffect } from 'react';
import { Calendar, Clock, CheckCircle, AlertCircle, Phone, Mail, FileText, Package, TrendingUp } from 'lucide-react';

interface AgendaItem {
  id: string;
  type: 'deadline' | 'follow-up' | 'quote-request' | 'call' | 'email' | 'document' | 'review';
  title: string;
  description: string;
  priority: 'urgent' | 'high' | 'medium' | 'low';
  dueDate: string;
  dueTime?: string;
  status: 'pending' | 'in-progress' | 'completed';
  relatedTo?: string;
  action: string;
}

interface AgendaSection {
  title: string;
  items: AgendaItem[];
  icon: React.ReactNode;
  color: string;
}

export const AgendaDashboard: React.FC = () => {
  const [selectedDay, setSelectedDay] = useState<'today' | 'tomorrow' | 'this-week'>('today');
  const [agendaItems, setAgendaItems] = useState<AgendaItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgenda();
    // Refresh every 15 minutes
    const interval = setInterval(fetchAgenda, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [selectedDay]);

  const fetchAgenda = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/agenda?view=${selectedDay}`);
      if (response.ok) {
        const data = await response.json();
        setAgendaItems(data.items || []);
      }
    } catch (error) {
      console.error('Failed to fetch agenda:', error);
      // Fallback to sample agenda
      setAgendaItems(getSampleAgenda());
    } finally {
      setLoading(false);
    }
  };

  const getSampleAgenda = (): AgendaItem[] => {
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

    if (selectedDay === 'today') {
      return [
        {
          id: '1',
          type: 'deadline',
          title: 'Submit NIH Surgical Supplies',
          description: '26-002571 - Surgicel products for patient care emergency',
          priority: 'urgent',
          dueDate: today,
          dueTime: '12:00 PM',
          status: 'in-progress',
          relatedTo: 'NIH Clinical Center',
          action: 'Generate PDF and submit by 10:45 AM'
        },
        {
          id: '2',
          type: 'call',
          title: 'Contact McKesson for Quote',
          description: 'Get final pricing and expedited shipping quote for Surgicel products',
          priority: 'urgent',
          dueDate: today,
          dueTime: '8:00 AM',
          status: 'pending',
          relatedTo: 'NIH Surgical Supplies',
          action: 'Call 1-800-625-3776 if no email by 8 AM'
        },
        {
          id: '3',
          type: 'follow-up',
          title: 'SAM.gov Opportunity Search',
          description: 'Run 62 searches for Intent to Sole Source and Sources Sought opportunities',
          priority: 'high',
          dueDate: today,
          dueTime: '1:00 PM',
          status: 'pending',
          action: 'Triple-search strategy: Intent, Sources Sought, Solicitations'
        },
        {
          id: '4',
          type: 'document',
          title: 'Start VA Orlando Courier Materials',
          description: 'Adapt VA Illiana capability statement for Orlando VA Healthcare',
          priority: 'high',
          dueDate: today,
          dueTime: '5:00 PM',
          status: 'pending',
          relatedTo: 'VA Orlando Courier (36C24826Q0302)',
          action: 'Reuse 90% of VA Illiana materials'
        },
        {
          id: '5',
          type: 'review',
          title: 'Add All Opportunities to NEXUS',
          description: 'Run Python script to add 6 EDWOSB opportunities to Airtable',
          priority: 'medium',
          dueDate: today,
          dueTime: '1:00 PM',
          status: 'pending',
          action: 'Run add_all_edwosb_opportunities_to_nexus.py'
        }
      ];
    } else if (selectedDay === 'tomorrow') {
      return [
        {
          id: '6',
          type: 'deadline',
          title: 'Complete VA Orlando Courier',
          description: 'Finalize and submit capability statement',
          priority: 'high',
          dueDate: tomorrow,
          status: 'pending',
          relatedTo: 'VA Orlando Courier',
          action: 'Finish materials and submit'
        },
        {
          id: '7',
          type: 'document',
          title: 'Start VA Moving & Storage',
          description: 'Create capability statement for warehousing and moving services',
          priority: 'high',
          dueDate: tomorrow,
          status: 'pending',
          relatedTo: 'VA Moving & Storage (36C25726Q0090)',
          action: 'Research subcontractors and create materials'
        }
      ];
    } else {
      return [
        {
          id: '8',
          type: 'deadline',
          title: 'VA Medical Waste Disposal',
          description: 'Submit capability statement - Deadline Feb 11',
          priority: 'urgent',
          dueDate: '2026-02-11',
          status: 'pending',
          relatedTo: 'VA Medical Waste (36C24126Q0238)',
          action: 'Create materials and submit by Feb 11'
        },
        {
          id: '9',
          type: 'deadline',
          title: 'VA Illiana Courier Response',
          description: 'Sources Sought response due - Deadline Feb 12',
          priority: 'high',
          dueDate: '2026-02-12',
          status: 'completed',
          relatedTo: 'VA Illiana (36C25226Q0235)',
          action: 'Already submitted ✅'
        },
        {
          id: '10',
          type: 'deadline',
          title: 'VA Orlando Courier Response',
          description: 'Solicitation response due - Deadline Feb 12',
          priority: 'high',
          dueDate: '2026-02-12',
          status: 'pending',
          relatedTo: 'VA Orlando (36C24826Q0302)',
          action: 'Submit by Feb 10-11'
        }
      ];
    }
  };

  const groupAgendaItems = (): AgendaSection[] => {
    const sections: { [key: string]: AgendaSection } = {
      urgent: {
        title: '🔴 Urgent - Do First',
        items: [],
        icon: <AlertCircle className="w-5 h-5 text-red-400" />,
        color: 'red'
      },
      deadlines: {
        title: '📅 Bid Deadlines',
        items: [],
        icon: <Clock className="w-5 h-5 text-blue-400" />,
        color: 'blue'
      },
      communication: {
        title: '📞 Calls & Emails',
        items: [],
        icon: <Phone className="w-5 h-5 text-purple-400" />,
        color: 'purple'
      },
      documents: {
        title: '📄 Documents to Create',
        items: [],
        icon: <FileText className="w-5 h-5 text-green-400" />,
        color: 'green'
      },
      followup: {
        title: '🔍 Follow-ups & Reviews',
        items: [],
        icon: <TrendingUp className="w-5 h-5 text-yellow-400" />,
        color: 'yellow'
      }
    };

    agendaItems.forEach(item => {
      if (item.priority === 'urgent') {
        sections.urgent.items.push(item);
      } else if (item.type === 'deadline') {
        sections.deadlines.items.push(item);
      } else if (item.type === 'call' || item.type === 'email') {
        sections.communication.items.push(item);
      } else if (item.type === 'document') {
        sections.documents.items.push(item);
      } else {
        sections.followup.items.push(item);
      }
    });

    return Object.values(sections).filter(section => section.items.length > 0);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'deadline': return <Clock className="w-4 h-4" />;
      case 'call': return <Phone className="w-4 h-4" />;
      case 'email': return <Mail className="w-4 h-4" />;
      case 'document': return <FileText className="w-4 h-4" />;
      case 'quote-request': return <Package className="w-4 h-4" />;
      case 'review': return <TrendingUp className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-400 bg-red-500/10 border-red-500';
      case 'high': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500';
      case 'medium': return 'text-blue-400 bg-blue-500/10 border-blue-500';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500';
    }
  };

  const toggleItemStatus = (itemId: string) => {
    try {
      setAgendaItems(items =>
        items.map(item =>
          item.id === itemId
            ? { ...item, status: item.status === 'completed' ? 'pending' : 'completed' }
            : item
        )
      );
      
      // Optional: Persist to backend
      // fetch(`http://localhost:8000/api/agenda/item/${itemId}/toggle`, { method: 'POST' })
      //   .catch(err => console.error('Failed to persist status:', err));
      
    } catch (error) {
      console.error('Error toggling item status:', error);
    }
  };

  const sections = groupAgendaItems();
  const completedCount = agendaItems.filter(item => item.status === 'completed').length;
  const totalCount = agendaItems.length;

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg">
      {/* Header */}
      <div className="border-b border-gray-700 bg-gray-750 p-6 rounded-t-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Your Agenda</h2>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">
              {completedCount}/{totalCount} completed
            </span>
            <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all"
                style={{ width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%` }}
              />
            </div>
          </div>
        </div>

        {/* Day Selector */}
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedDay('today')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedDay === 'today'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Today
          </button>
          <button
            onClick={() => setSelectedDay('tomorrow')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedDay === 'tomorrow'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Tomorrow
          </button>
          <button
            onClick={() => setSelectedDay('this-week')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedDay === 'this-week'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            This Week
          </button>
        </div>
      </div>

      {/* Agenda Sections */}
      <div className="p-6 space-y-6">
        {loading ? (
          <div className="text-center py-12 text-gray-400">
            Loading agenda...
          </div>
        ) : sections.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
            <p className="text-xl font-semibold text-white mb-2">All clear!</p>
            <p className="text-gray-400">No tasks for {selectedDay}</p>
          </div>
        ) : (
          sections.map((section, index) => (
            <div key={index} className="space-y-3">
              <div className="flex items-center gap-2">
                {section.icon}
                <h3 className="text-lg font-semibold text-white">{section.title}</h3>
                <span className="text-sm text-gray-400">({section.items.length})</span>
              </div>

              <div className="space-y-2">
                {section.items.map(item => (
                  <div
                    key={item.id}
                    className={`bg-gray-750 border-l-4 rounded-lg p-4 transition ${
                      item.status === 'completed'
                        ? 'opacity-50 border-green-500'
                        : getPriorityColor(item.priority)
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Checkbox */}
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          toggleItemStatus(item.id);
                        }}
                        className={`mt-1 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition ${
                          item.status === 'completed'
                            ? 'bg-green-500 border-green-500'
                            : 'border-gray-500 hover:border-blue-400'
                        }`}
                        type="button"
                      >
                        {item.status === 'completed' && (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                      </button>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div className="flex items-center gap-2">
                            {getTypeIcon(item.type)}
                            <h4 className={`font-semibold ${
                              item.status === 'completed' ? 'line-through text-gray-400' : 'text-white'
                            }`}>
                              {item.title}
                            </h4>
                          </div>
                          
                          {item.dueTime && (
                            <span className="text-sm text-gray-400 flex-shrink-0">
                              {item.dueTime}
                            </span>
                          )}
                        </div>

                        <p className="text-sm text-gray-300 mb-2">{item.description}</p>

                        {item.relatedTo && (
                          <div className="text-xs text-gray-400 mb-2">
                            Related to: {item.relatedTo}
                          </div>
                        )}

                        <div className="bg-gray-700 px-3 py-1.5 rounded text-sm text-gray-200">
                          <span className="font-medium">Action:</span> {item.action}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AgendaDashboard;
