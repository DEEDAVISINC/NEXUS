import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface ATLASSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in-progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  owner: string;
  dueDate: string;
  progress: number;
  budget?: number;
  description?: string;
  project?: string;
  subtasks?: Array<{id: string, title: string, completed: boolean}>;
  comments?: Array<{id: string, user: string, text: string, time: string}>;
}

const ATLASSystem: React.FC<ATLASSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  // Task Board State
  const [boardView, setBoardView] = useState<'board' | 'timeline' | 'calendar' | 'list'>('board');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showCalendarMenu, setShowCalendarMenu] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);

  // Projects State
  const [projects, setProjects] = useState<any[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<any | null>(null);
  const [projectFormData, setProjectFormData] = useState({
    name: '',
    client: '',
    type: 'Consulting',
    industry: '',
    scope: '',
    budget: 0,
    timeline: '',
    startDate: '',
    priority: 'Medium'
  });

  // RFP Analysis State
  const [rfpAnalysis, setRfpAnalysis] = useState<any | null>(null);
  const [analyzingRfp, setAnalyzingRfp] = useState(false);

  // WBS Generator State
  const [wbsResult, setWbsResult] = useState<any | null>(null);
  const [generatingWbs, setGeneratingWbs] = useState(false);
  const [wbsProjectId, setWbsProjectId] = useState<string>('');

  // Change Orders State
  const [changeOrders, setChangeOrders] = useState<any[]>([]);
  const [showChangeOrderModal, setShowChangeOrderModal] = useState(false);
  const [changeOrderFormData, setChangeOrderFormData] = useState({
    title: '',
    description: '',
    projectId: '',
    impactBudget: 0,
    impactTimeline: ''
  });

  // Load tasks from Airtable on mount
  useEffect(() => {
    if (activeTab === 'task-board') {
      loadTasks();
    }
  }, [activeTab]);

  // Load projects when projects tab is active
  useEffect(() => {
    if (activeTab === 'projects') {
      fetchProjects();
    }
  }, [activeTab]);

  // Load change orders when change orders tab is active
  useEffect(() => {
    if (activeTab === 'change-orders') {
      fetchChangeOrders();
    }
  }, [activeTab]);

  // Load projects when WBS Generator tab is active
  useEffect(() => {
    if (activeTab === 'wbs-generator') {
      fetchProjects();
    }
  }, [activeTab]);

  const loadTasks = async () => {
    try {
      setTasksLoading(true);
      const response = await api.getTasks();
      if (response.tasks && response.tasks.length > 0) {
        setTasks(response.tasks);
      } else {
        // Load sample tasks if Airtable is empty
        const sampleTasks: Task[] = [
          { id: '1', title: 'Site Survey - Wisconsin Locations', status: 'in-progress', priority: 'high', owner: 'Dee Davis', dueDate: '2026-01-15', progress: 65, budget: 5000, project: 'Wisconsin NEMT', description: 'Complete site surveys at all 3 Wisconsin locations' },
          { id: '2', title: 'Data Migration Planning', status: 'todo', priority: 'high', owner: 'Mike Chen', dueDate: '2026-01-17', progress: 0, budget: 8000, project: 'Wisconsin NEMT' },
          { id: '3', title: 'Training Materials Development', status: 'todo', priority: 'medium', owner: 'Sarah Johnson', dueDate: '2026-01-20', progress: 0, budget: 3000, project: 'Wisconsin NEMT' },
          { id: '4', title: 'Security Compliance Review', status: 'done', priority: 'high', owner: 'Dee Davis', dueDate: '2026-01-05', progress: 100, budget: 2500, project: 'Wisconsin NEMT' },
          { id: '5', title: 'Database Schema Design', status: 'in-progress', priority: 'high', owner: 'Mike Chen', dueDate: '2026-01-16', progress: 45, budget: 6000, project: 'Wisconsin NEMT' },
          { id: '6', title: 'UI/UX Design Review', status: 'review', priority: 'medium', owner: 'Sarah Johnson', dueDate: '2026-01-14', progress: 90, budget: 4000, project: 'Wisconsin NEMT' },
          { id: '7', title: 'Client Kickoff Meeting Prep', status: 'done', priority: 'high', owner: 'Dee Davis', dueDate: '2026-01-03', progress: 100, budget: 500, project: 'Wisconsin NEMT' },
          { id: '8', title: 'API Integration Testing', status: 'todo', priority: 'medium', owner: 'Mike Chen', dueDate: '2026-01-22', progress: 0, budget: 7000, project: 'Wisconsin NEMT' },
        ];
        setTasks(sampleTasks);
      }
      setTasksLoading(false);
    } catch (error) {
      console.error('Error loading tasks:', error);
      setTasksLoading(false);
    }
  };

  const saveTask = async (task: Task) => {
    try {
      if (task.id && task.id.startsWith('rec')) {
        // Existing Airtable task - update it
        await api.updateTask(task.id, {
          title: task.title,
          status: task.status,
          priority: task.priority,
          owner: task.owner,
          dueDate: task.dueDate,
          progress: task.progress,
          budget: task.budget,
          description: task.description,
          project: task.project
        });
      } else {
        // New task - create in Airtable
        const response = await api.createTask({
          title: task.title,
          status: task.status,
          priority: task.priority,
          owner: task.owner,
          dueDate: task.dueDate,
          progress: task.progress,
          budget: task.budget,
          description: task.description,
          project: task.project
        });
        // Update task with Airtable ID
        if (response.task && response.task.id) {
          task.id = response.task.id;
        }
      }
      return true;
    } catch (error) {
      console.error('Error saving task:', error);
      return false;
    }
  };

  const deleteTaskFromDB = async (taskId: string) => {
    try {
      if (taskId.startsWith('rec')) {
        await api.deleteTask(taskId);
      }
      return true;
    } catch (error) {
      console.error('Error deleting task:', error);
      return false;
    }
  };

  // Generate .ics file for macOS Calendar
  const generateICS = (task: Task) => {
    const startDate = new Date(task.dueDate);
    const endDate = new Date(startDate.getTime() + 60 * 60 * 1000); // 1 hour duration
    
    const formatDate = (date: Date) => {
      return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    };

    const priorityMap = {
      'urgent': '1',
      'high': '3',
      'medium': '5',
      'low': '7'
    };

    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NEXUS//ATLAS PM//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:${task.id}@nexus.local
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(startDate)}
DTEND:${formatDate(endDate)}
SUMMARY:${task.title}
DESCRIPTION:${task.description || 'ATLAS PM Task'}\\n\\nProject: ${task.project || 'N/A'}\\nOwner: ${task.owner}\\nPriority: ${task.priority.toUpperCase()}\\nProgress: ${task.progress}%${task.budget ? '\\nBudget: $' + task.budget.toLocaleString() : ''}
LOCATION:NEXUS - ATLAS PM
PRIORITY:${priorityMap[task.priority]}
STATUS:${task.status === 'done' ? 'COMPLETED' : 'CONFIRMED'}
PERCENT-COMPLETE:${task.progress}
ORGANIZER:CN=${task.owner}
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Task Due: ${task.title}
END:VALARM
END:VEVENT
END:VCALENDAR`;

    return icsContent;
  };

  const downloadICS = (task: Task) => {
    const icsContent = generateICS(task);
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${task.title.replace(/[^a-z0-9]/gi, '_')}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    setNotification({ message: 'Calendar event downloaded! Opening in Calendar...', type: 'success' });
    setTimeout(() => setNotification(null), 3000);
  };

  const downloadAllTasksICS = () => {
    const allEvents = tasks.filter(t => t.dueDate).map((task, index) => {
      const startDate = new Date(task.dueDate);
      const endDate = new Date(startDate.getTime() + 60 * 60 * 1000);
      
      const formatDate = (date: Date) => {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
      };

      const priorityMap = {
        'urgent': '1',
        'high': '3',
        'medium': '5',
        'low': '7'
      };

      return `BEGIN:VEVENT
UID:${task.id}@nexus.local
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(startDate)}
DTEND:${formatDate(endDate)}
SUMMARY:${task.title}
DESCRIPTION:${task.description || 'ATLAS PM Task'}\\n\\nProject: ${task.project || 'N/A'}\\nOwner: ${task.owner}\\nPriority: ${task.priority.toUpperCase()}\\nProgress: ${task.progress}%${task.budget ? '\\nBudget: $' + task.budget.toLocaleString() : ''}
LOCATION:NEXUS - ATLAS PM
PRIORITY:${priorityMap[task.priority]}
STATUS:${task.status === 'done' ? 'COMPLETED' : 'CONFIRMED'}
PERCENT-COMPLETE:${task.progress}
ORGANIZER:CN=${task.owner}
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Task Due: ${task.title}
END:VALARM
END:VEVENT`;
    }).join('\n');

    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NEXUS//ATLAS PM//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
${allEvents}
END:VCALENDAR`;

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ATLAS_PM_All_Tasks.ics';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    setNotification({ message: `${tasks.filter(t => t.dueDate).length} tasks exported to Calendar!`, type: 'success' });
    setTimeout(() => setNotification(null), 3000);
  };

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'projects', label: '📋 Projects' },
    { id: 'task-board', label: '📋 Task Board' },
    { id: 'rfp-analysis', label: '🔍 RFP Analysis' },
    { id: 'wbs-generator', label: '🏗️ WBS Generator' },
    { id: 'change-orders', label: '📝 Change Orders' },
    { id: 'documents', label: '📄 Documents' },
    { id: 'analytics', label: '📈 Analytics' }
  ];

  const stats = [
    { label: 'Active Projects', value: '3', subtext: 'In Progress', gradient: 'from-blue-600 to-blue-800' },
    { label: 'RFPs Analyzed', value: '12', subtext: 'This Quarter', gradient: 'from-green-600 to-green-800' },
    { label: 'WBS Generated', value: '8', subtext: 'Complete', gradient: 'from-purple-600 to-purple-800' },
    { label: 'Total Value', value: '$2.4M', subtext: 'Active Contracts', gradient: 'from-yellow-600 to-yellow-800' }
  ];

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      showNotification(`Selected: ${file.name}`, 'success');
    } else {
      showNotification('Please select a PDF file', 'error');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      showNotification(`Selected: ${file.name}`, 'success');
    } else {
      showNotification('Please drop a PDF file', 'error');
    }
  };

  // Projects Functions
  const fetchProjects = async () => {
    setProjectsLoading(true);
    try {
      const response = await api.getProjects();
      setProjects(response.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
      setProjects([]);
    } finally {
      setProjectsLoading(false);
    }
  };

  const createProject = async () => {
    try {
      const response = await api.createProject(projectFormData);
      if (response.project) {
        showNotification('✅ Project created!', 'success');
        setShowProjectModal(false);
        resetProjectForm();
        fetchProjects();
      }
    } catch (error) {
      showNotification('❌ Error creating project', 'error');
    }
  };

  const updateProject = async (projectId: string) => {
    try {
      const response = await api.updateProject(projectId, projectFormData);
      if (response.success) {
        showNotification('✅ Project updated!', 'success');
        setShowProjectModal(false);
        resetProjectForm();
        fetchProjects();
      }
    } catch (error) {
      showNotification('❌ Error updating project', 'error');
    }
  };

  const deleteProject = async (projectId: string) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    try {
      // Note: DELETE endpoint needs to be added to backend if not exists
      // For now, we'll handle it via update with status = 'Deleted'
      showNotification('⚠️ Delete functionality coming soon', 'error');
    } catch (error) {
      showNotification('❌ Error deleting project', 'error');
    }
  };

  const resetProjectForm = () => {
    setProjectFormData({
      name: '',
      client: '',
      type: 'Consulting',
      industry: '',
      scope: '',
      budget: 0,
      timeline: '',
      startDate: '',
      priority: 'Medium'
    });
    setSelectedProject(null);
  };

  const openProjectModal = (project?: any) => {
    if (project) {
      setSelectedProject(project);
      setProjectFormData({
        name: project.name || '',
        client: project.client || '',
        type: project.type || 'Consulting',
        industry: project.industry || '',
        scope: project.scope || '',
        budget: project.budget || 0,
        timeline: project.timeline || '',
        startDate: project.startDate || '',
        priority: project.priority || 'Medium'
      });
    } else {
      resetProjectForm();
    }
    setShowProjectModal(true);
  };

  // RFP Analysis Functions
  const analyzeRFP = async () => {
    if (!selectedFile) {
      showNotification('Please select a PDF file first', 'error');
      return;
    }

    setAnalyzingRfp(true);
    
    try {
      // In a real implementation, you'd read the PDF content
      // For now, we'll send a placeholder
      const rfpContent = `RFP Document: ${selectedFile.name}`;
      
      const response = await api.analyzeRfp(rfpContent);
      
      if (response.error) {
        showNotification(`❌ Error: ${response.error}`, 'error');
      } else {
        setRfpAnalysis(response);
        showNotification('✅ RFP analyzed successfully!', 'success');
        setSelectedFile(null);
        const fileInput = document.getElementById('rfpFileInput') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }
    } catch (error) {
      showNotification('❌ Error analyzing RFP', 'error');
    } finally {
      setAnalyzingRfp(false);
    }
  };

  // WBS Generator Functions
  const generateWBS = async (projectId: string) => {
    setGeneratingWbs(true);
    setWbsProjectId(projectId);
    
    try {
      const response = await api.generateWbs(projectId);
      
      if (response.error) {
        showNotification(`❌ Error: ${response.error}`, 'error');
      } else {
        setWbsResult(response);
        showNotification('✅ WBS generated successfully!', 'success');
      }
    } catch (error) {
      showNotification('❌ Error generating WBS', 'error');
    } finally {
      setGeneratingWbs(false);
    }
  };

  // Change Orders Functions
  const fetchChangeOrders = async () => {
    try {
      const response = await api.getChangeOrders();
      setChangeOrders(response.change_orders || []);
    } catch (error) {
      console.error('Error fetching change orders:', error);
      setChangeOrders([]);
    }
  };

  const createChangeOrder = async () => {
    try {
      const response = await api.createChangeOrder(changeOrderFormData);
      if (response.change_order) {
        showNotification('✅ Change order created!', 'success');
        setShowChangeOrderModal(false);
        resetChangeOrderForm();
        fetchChangeOrders();
      }
    } catch (error) {
      showNotification('❌ Error creating change order', 'error');
    }
  };

  const resetChangeOrderForm = () => {
    setChangeOrderFormData({
      title: '',
      description: '',
      projectId: '',
      impactBudget: 0,
      impactTimeline: ''
    });
  };

  const analyzeChangeRequest = async (description: string, projectId: string) => {
    try {
      const response = await api.analyzeChangeRequest(description, projectId);
      if (response.error) {
        showNotification(`❌ Error: ${response.error}`, 'error');
      } else {
        showNotification('✅ Change request analyzed!', 'success');
        return response;
      }
    } catch (error) {
      showNotification('❌ Error analyzing change request', 'error');
    }
  };

  return (
    <div className="relative">
      {/* System Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* TAB: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🏗️ ATLAS PM - Project Management Command Center</h2>
              <p className="text-gray-400">AI-powered RFP analysis, WBS generation, and change order management</p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              {stats.map((stat, index) => (
                <div key={index} className={`bg-gradient-to-br ${stat.gradient} p-6 rounded-xl`}>
                  <h3 className="text-sm font-semibold text-white/80 mb-2">{stat.label}</h3>
                  <p className="text-4xl font-bold mb-1">{stat.value}</p>
                  <p className="text-sm text-white/70">{stat.subtext}</p>
                </div>
              ))}
            </div>

            {/* Project Status Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Active Projects */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">📋 Active Projects</h3>
                <div className="space-y-3">
                  <div className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h4 className="font-bold text-blue-400">Wisconsin Emergency Logistics</h4>
                        <p className="text-sm text-gray-400">County-wide emergency response system</p>
                      </div>
                      <span className="bg-green-500/20 text-green-400 text-xs font-bold px-2 py-1 rounded">ACTIVE</span>
                    </div>
                    <div className="flex justify-between items-center text-sm mt-2">
                      <span className="text-gray-400">Progress: 65%</span>
                      <span className="text-green-400 font-bold">$1.2M</span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                    </div>
                  </div>

                  <div className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h4 className="font-bold text-purple-400">Michigan NEMT Modernization</h4>
                        <p className="text-sm text-gray-400">Transportation system upgrade</p>
                      </div>
                      <span className="bg-yellow-500/20 text-yellow-400 text-xs font-bold px-2 py-1 rounded">PLANNING</span>
                    </div>
                    <div className="flex justify-between items-center text-sm mt-2">
                      <span className="text-gray-400">Kickoff: Mar 2026</span>
                      <span className="text-green-400 font-bold">$850K</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI System Status */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">🤖 AI Project Management System</h3>
                <div className="space-y-4">
                  <div className="bg-green-900/30 border border-green-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <p className="font-semibold">RFP Analysis Engine</p>
                      </div>
                      <span className="text-xs bg-green-500/20 px-2 py-1 rounded text-green-400">ONLINE</span>
                    </div>
                    <p className="text-xs text-gray-400">Analyzes RFPs for win probability and risk assessment</p>
                  </div>

                  <div className="bg-green-900/30 border border-green-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <p className="font-semibold">WBS Generator</p>
                      </div>
                      <span className="text-xs bg-green-500/20 px-2 py-1 rounded text-green-400">ONLINE</span>
                    </div>
                    <p className="text-xs text-gray-400">Creates detailed work breakdown structures automatically</p>
                  </div>

                  <div className="bg-blue-900/30 border border-blue-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">💡</span>
                      <p className="font-semibold text-blue-400">AI Suggestion</p>
                    </div>
                    <p className="text-sm text-gray-300 mb-3">The Michigan RFP has a 78% win probability. Consider prioritizing this project.</p>
                    <button 
                      onClick={() => setActiveTab('rfp-analysis')}
                      className="w-full bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg text-sm font-semibold transition"
                    >
                      Analyze Michigan RFP →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <button 
                onClick={() => setActiveTab('rfp-analysis')}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 px-6 py-4 rounded-lg font-semibold transition"
              >
                🔍 Analyze New RFP
              </button>
              <button 
                onClick={() => setActiveTab('wbs-generator')}
                className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 px-6 py-4 rounded-lg font-semibold transition"
              >
                🏗️ Generate WBS
              </button>
              <button 
                onClick={() => setActiveTab('change-orders')}
                className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 px-6 py-4 rounded-lg font-semibold transition"
              >
                📝 Manage Change Orders
              </button>
            </div>
          </div>
        )}

        {/* TAB: RFP ANALYSIS */}
        {activeTab === 'rfp-analysis' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🔍 RFP Analysis Engine</h2>
              <p className="text-gray-400">AI-powered analysis of government RFPs for win probability and risk assessment</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
              <div 
                className={`border-3 border-dashed ${isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-700/30'} p-12 rounded-xl text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800 transition`}
                onClick={() => document.getElementById('rfpFileInput')?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-xl font-bold mb-2 text-blue-400">Drop RFP PDF here or click to browse</h3>
                <p className="text-gray-400 mb-4">AI will analyze for: Requirements, Budget, Timeline, Competition, Win Probability</p>
                <input 
                  type="file" 
                  id="rfpFileInput" 
                  accept=".pdf" 
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>

              {selectedFile && (
                <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
                  <p className="text-green-400 font-semibold">
                    ✅ {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                </div>
              )}

              {selectedFile && !analyzingRfp && (
                <div className="mt-6 text-center">
                  <button 
                    onClick={analyzeRFP}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-bold text-lg transition"
                  >
                    🤖 Analyze RFP with AI
                  </button>
                </div>
              )}

              {analyzingRfp && (
                <div className="mt-6">
                  <div className="bg-blue-900/30 border border-blue-700 p-6 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <div>
                        <h4 className="font-bold text-blue-400 mb-1">AI Analyzing RFP...</h4>
                        <p className="text-sm text-gray-400">Evaluating requirements, budget, timeline, and competition</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* RFP Analysis Results */}
            {rfpAnalysis && !rfpAnalysis.error && (
              <div className="mt-6 space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-2xl font-bold">📊 Analysis Results</h3>
                  <button 
                    onClick={() => {
                      setRfpAnalysis(null);
                      setSelectedFile(null);
                    }}
                    className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                  >
                    Analyze New RFP
                  </button>
                </div>

                {/* Win Probability & Risk Score */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                    <h4 className="text-sm font-semibold text-white/80 mb-2">Win Probability</h4>
                    <p className="text-5xl font-bold mb-1">{rfpAnalysis.win_probability || 'N/A'}%</p>
                    <p className="text-sm text-white/70">{rfpAnalysis.win_strategy?.slice(0, 50) || 'Analysis complete'}...</p>
                  </div>
                  <div className="bg-gradient-to-br from-red-600 to-red-800 p-6 rounded-xl">
                    <h4 className="text-sm font-semibold text-white/80 mb-2">Risk Level</h4>
                    <p className="text-5xl font-bold mb-1">{rfpAnalysis.risk_level || 'N/A'}</p>
                    <p className="text-sm text-white/70">{rfpAnalysis.risk_assessment?.slice(0, 50) || 'Risk assessed'}...</p>
                  </div>
                </div>

                {/* Key Requirements */}
                {rfpAnalysis.key_requirements && (
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-blue-400">📋 Key Requirements</h4>
                    <ul className="space-y-2">
                      {(Array.isArray(rfpAnalysis.key_requirements) ? rfpAnalysis.key_requirements : [rfpAnalysis.key_requirements]).map((req: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-green-400 mt-1">✓</span>
                          <span className="text-gray-300">{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Win Strategy */}
                {rfpAnalysis.win_strategy && (
                  <div className="bg-blue-900/30 border border-blue-700 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-blue-400">🎯 Win Strategy</h4>
                    <p className="text-gray-300 whitespace-pre-wrap">{rfpAnalysis.win_strategy}</p>
                  </div>
                )}

                {/* Risk Assessment */}
                {rfpAnalysis.risk_assessment && (
                  <div className="bg-red-900/30 border border-red-700 rounded-xl p-6">
                    <h4 className="text-xl font-bold mb-4 text-red-400">⚠️ Risk Assessment</h4>
                    <p className="text-gray-300 whitespace-pre-wrap">{rfpAnalysis.risk_assessment}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB: WBS GENERATOR */}
        {activeTab === 'wbs-generator' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🏗️ WBS Generator</h2>
              <p className="text-gray-400">AI-powered Work Breakdown Structure creation for project planning</p>
            </div>

            {/* Load Projects First */}
            {projects.length === 0 && (
              <div className="mb-6 bg-yellow-900/30 border border-yellow-700 rounded-xl p-6">
                <p className="text-yellow-400 font-semibold mb-2">⚠️ No Projects Found</p>
                <p className="text-gray-300 text-sm mb-4">Create a project first to generate a WBS.</p>
                <button 
                  onClick={() => {
                    fetchProjects();
                    setActiveTab('projects');
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  Go to Projects →
                </button>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">Select Project</h3>
                <div className="space-y-4">
                  {projects.length > 0 ? (
                    <>
                      <div>
                        <label className="block text-sm font-semibold mb-2">Choose Project</label>
                        <select 
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                          value={wbsProjectId}
                          onChange={(e) => setWbsProjectId(e.target.value)}
                        >
                          <option value="">Select a project...</option>
                          {projects.map(project => (
                            <option key={project.id} value={project.id}>
                              {project.name} - {project.client}
                            </option>
                          ))}
                        </select>
                      </div>
                      <button 
                        onClick={() => wbsProjectId && generateWBS(wbsProjectId)}
                        disabled={!wbsProjectId || generatingWbs}
                        className={`w-full ${
                          !wbsProjectId || generatingWbs 
                            ? 'bg-gray-600 cursor-not-allowed' 
                            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                        } px-6 py-3 rounded-lg font-bold transition`}
                      >
                        {generatingWbs ? '⏳ Generating...' : '🤖 Generate WBS'}
                      </button>
                    </>
                  ) : (
                    <p className="text-gray-400 text-center py-4">No projects available. Create a project first.</p>
                  )}
                </div>
              </div>

              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">Generated WBS</h3>
                {generatingWbs ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                      <p className="text-gray-400">AI generating WBS...</p>
                    </div>
                  </div>
                ) : wbsResult && !wbsResult.error ? (
                  <div className="space-y-3 max-h-[500px] overflow-y-auto">
                    {wbsResult.wbs_items && Array.isArray(wbsResult.wbs_items) ? (
                      wbsResult.wbs_items.map((item: any, idx: number) => (
                        <div key={idx} className="bg-gray-700/50 p-4 rounded-lg">
                          <h4 className="font-bold text-blue-400 mb-2">{item.code || `${idx + 1}.0`} {item.title || item.name}</h4>
                          {item.description && (
                            <p className="text-sm text-gray-300 mb-2">{item.description}</p>
                          )}
                          {item.subtasks && item.subtasks.length > 0 && (
                            <ul className="text-sm text-gray-300 space-y-1 ml-4">
                              {item.subtasks.map((subtask: any, subIdx: number) => (
                                <li key={subIdx}>• {subtask.code || `${idx + 1}.${subIdx + 1}`} {subtask.title || subtask.name}</li>
                              ))}
                            </ul>
                          )}
                          {item.duration && (
                            <div className="mt-2 text-xs text-gray-400">
                              Duration: {item.duration} • Budget: ${item.budget?.toLocaleString() || 'N/A'}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="bg-gray-700/50 p-4 rounded-lg">
                        <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                          {typeof wbsResult === 'string' ? wbsResult : JSON.stringify(wbsResult, null, 2)}
                        </pre>
                      </div>
                    )}
                    {wbsResult.wbs_items && (
                      <button 
                        onClick={() => {
                          const wbsText = wbsResult.wbs_items.map((item: any) => 
                            `${item.code || ''} ${item.title || item.name}\n${item.description || ''}`
                          ).join('\n\n');
                          const blob = new Blob([wbsText], { type: 'text/plain' });
                          const url = window.URL.createObjectURL(blob);
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = 'WBS.txt';
                          link.click();
                          window.URL.revokeObjectURL(url);
                          showNotification('📄 WBS exported!', 'success');
                        }}
                        className="w-full mt-4 bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-semibold transition"
                      >
                        📄 Export WBS Document
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4 opacity-20">🏗️</div>
                    <p className="text-gray-400">Select a project and generate WBS to see results</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB: PROJECTS */}
        {activeTab === 'projects' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">📋 Project Portfolio</h2>
                <p className="text-gray-400">Manage all active and completed projects</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => openProjectModal()}
                  className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  ➕ New Project
                </button>
                <button 
                  onClick={fetchProjects}
                  className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold transition"
                >
                  🔄 Refresh
                </button>
              </div>
            </div>

            {projectsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400">Loading projects...</p>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-xl overflow-hidden">
                {projects.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-700">
                        <tr>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Project</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Client</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Status</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Budget</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Progress</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Priority</th>
                          <th className="text-left px-6 py-4 font-semibold text-gray-300">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {projects.map(project => (
                          <tr key={project.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                            <td className="px-6 py-4">
                              <div className="font-bold text-blue-400">{project.name}</div>
                              <div className="text-sm text-gray-400">{project.type || 'Consulting'}</div>
                            </td>
                            <td className="px-6 py-4 text-gray-300">{project.client || '-'}</td>
                            <td className="px-6 py-4">
                              <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                project.status === 'Active' || project.status === 'In Progress' ? 'bg-green-500/20 text-green-400' :
                                project.status === 'Planning' ? 'bg-yellow-500/20 text-yellow-400' :
                                project.status === 'Completed' ? 'bg-blue-500/20 text-blue-400' :
                                'bg-gray-500/20 text-gray-400'
                              }`}>
                                {project.status || 'Planning'}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-green-400 font-bold">
                                ${(project.budget || 0).toLocaleString()}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-2">
                                <span className="text-sm">{project.completion_percentage || 0}%</span>
                                <div className="w-20 bg-gray-600 rounded-full h-2">
                                  <div 
                                    className="bg-blue-500 h-2 rounded-full" 
                                    style={{ width: `${project.completion_percentage || 0}%` }}
                                  ></div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <span className={`text-xs font-semibold px-2 py-1 rounded ${
                                project.priority === 'High' || project.priority === 'Urgent' ? 'bg-red-500/20 text-red-400' :
                                project.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                'bg-gray-500/20 text-gray-400'
                              }`}>
                                {project.priority || 'Medium'}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex gap-2">
                                <button 
                                  onClick={() => openProjectModal(project)}
                                  className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm font-semibold transition"
                                >
                                  Edit
                                </button>
                                <button 
                                  onClick={() => generateWBS(project.id)}
                                  className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm font-semibold transition"
                                >
                                  WBS
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4 opacity-20">📋</div>
                    <p className="text-gray-500 font-semibold mb-4">No projects yet</p>
                    <p className="text-sm text-gray-600 mb-6">Create your first project to start managing it with ATLAS PM</p>
                    <button 
                      onClick={() => openProjectModal()}
                      className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                    >
                      ➕ Create First Project
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Project Modal */}
            {showProjectModal && (
              <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-y-auto">
                <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
                  <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 sticky top-0 z-10">
                    <div className="flex items-center justify-between">
                      <h2 className="text-2xl font-bold">{selectedProject ? 'Edit Project' : 'New Project'}</h2>
                      <button 
                        onClick={() => {
                          setShowProjectModal(false);
                          resetProjectForm();
                        }}
                        className="text-white hover:text-gray-300 text-3xl font-bold"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  <div className="p-6 space-y-4">
                    <div>
                      <label className="block text-sm font-semibold mb-2">Project Name *</label>
                      <input 
                        type="text"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        value={projectFormData.name}
                        onChange={(e) => setProjectFormData({...projectFormData, name: e.target.value})}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold mb-2">Client Name *</label>
                        <input 
                          type="text"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          value={projectFormData.client}
                          onChange={(e) => setProjectFormData({...projectFormData, client: e.target.value})}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold mb-2">Project Type</label>
                        <select 
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          value={projectFormData.type}
                          onChange={(e) => setProjectFormData({...projectFormData, type: e.target.value})}
                        >
                          <option value="Consulting">Consulting</option>
                          <option value="IT Development">IT Development</option>
                          <option value="Implementation">Implementation</option>
                          <option value="Training">Training</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold mb-2">Industry</label>
                      <input 
                        type="text"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        value={projectFormData.industry}
                        onChange={(e) => setProjectFormData({...projectFormData, industry: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold mb-2">Project Scope</label>
                      <textarea 
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        rows={3}
                        value={projectFormData.scope}
                        onChange={(e) => setProjectFormData({...projectFormData, scope: e.target.value})}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold mb-2">Budget</label>
                        <input 
                          type="number"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          value={projectFormData.budget}
                          onChange={(e) => setProjectFormData({...projectFormData, budget: parseFloat(e.target.value) || 0})}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold mb-2">Priority</label>
                        <select 
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          value={projectFormData.priority}
                          onChange={(e) => setProjectFormData({...projectFormData, priority: e.target.value})}
                        >
                          <option value="Low">Low</option>
                          <option value="Medium">Medium</option>
                          <option value="High">High</option>
                          <option value="Urgent">Urgent</option>
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold mb-2">Timeline</label>
                        <input 
                          type="text"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          placeholder="e.g., 6 months"
                          value={projectFormData.timeline}
                          onChange={(e) => setProjectFormData({...projectFormData, timeline: e.target.value})}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold mb-2">Start Date</label>
                        <input 
                          type="date"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                          value={projectFormData.startDate}
                          onChange={(e) => setProjectFormData({...projectFormData, startDate: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="flex gap-2 pt-4">
                      <button 
                        onClick={() => selectedProject ? updateProject(selectedProject.id) : createProject()}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                      >
                        {selectedProject ? 'Update' : 'Create'}
                      </button>
                      <button 
                        onClick={() => {
                          setShowProjectModal(false);
                          resetProjectForm();
                        }}
                        className="flex-1 bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB: CHANGE ORDERS */}
        {activeTab === 'change-orders' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">📝 Change Order Management</h2>
                <p className="text-gray-400">Track and analyze project change requests</p>
              </div>
              <button 
                onClick={() => {
                  fetchProjects();
                  setShowChangeOrderModal(true);
                }}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                ➕ New Change Order
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">Change Orders</h3>
                {changeOrders.length > 0 ? (
                  <div className="space-y-3">
                    {changeOrders.map((co: any) => (
                      <div key={co.id} className={`border px-4 py-4 rounded-lg ${
                        co.status === 'Pending' ? 'bg-yellow-900/30 border-yellow-700' :
                        co.status === 'Approved' ? 'bg-green-900/30 border-green-700' :
                        'bg-gray-700/50 border-gray-600'
                      }`}>
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className={`font-bold ${
                              co.status === 'Pending' ? 'text-yellow-400' :
                              co.status === 'Approved' ? 'text-green-400' :
                              'text-gray-400'
                            }`}>{co.title || co.name}</h4>
                            <p className="text-sm text-gray-400">{co.project_name || 'N/A'}</p>
                          </div>
                          <span className={`text-xs font-bold px-2 py-1 rounded ${
                            co.status === 'Pending' ? 'bg-yellow-500/20 text-yellow-400' :
                            co.status === 'Approved' ? 'bg-green-500/20 text-green-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>{co.status || 'Pending'}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm mt-2">
                          <span className="text-gray-400">Impact: +${(co.impact_budget || 0).toLocaleString()}</span>
                          <button 
                            onClick={() => analyzeChangeRequest(co.description || co.title, co.project_id || '')}
                            className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-semibold transition"
                          >
                            Analyze
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-2 opacity-20">📝</div>
                    <p className="text-gray-400 text-sm">No change orders yet</p>
                  </div>
                )}
              </div>

              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">Create Change Order</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">Project</label>
                    <select 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                      value={changeOrderFormData.projectId}
                      onChange={(e) => setChangeOrderFormData({...changeOrderFormData, projectId: e.target.value})}
                    >
                      <option value="">Select project...</option>
                      {projects.map(project => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">Title</label>
                    <input 
                      type="text"
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                      value={changeOrderFormData.title}
                      onChange={(e) => setChangeOrderFormData({...changeOrderFormData, title: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">Description</label>
                    <textarea 
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                      rows={3}
                      value={changeOrderFormData.description}
                      onChange={(e) => setChangeOrderFormData({...changeOrderFormData, description: e.target.value})}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold mb-2">Budget Impact</label>
                      <input 
                        type="number"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        value={changeOrderFormData.impactBudget}
                        onChange={(e) => setChangeOrderFormData({...changeOrderFormData, impactBudget: parseFloat(e.target.value) || 0})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold mb-2">Timeline Impact</label>
                      <input 
                        type="text"
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                        placeholder="e.g., +2 weeks"
                        value={changeOrderFormData.impactTimeline}
                        onChange={(e) => setChangeOrderFormData({...changeOrderFormData, impactTimeline: e.target.value})}
                      />
                    </div>
                  </div>
                  <button 
                    onClick={createChangeOrder}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition"
                  >
                    ➕ Create Change Order
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: DOCUMENTS */}
        {activeTab === 'documents' && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">📄 Documents</h2>
                <p className="text-gray-400">Manage project documents and files</p>
              </div>
              <button 
                onClick={() => {
                  const input = document.createElement('input');
                  input.type = 'file';
                  input.multiple = true;
                  input.onchange = () => {
                    showNotification('📄 Document upload feature coming soon!', 'success');
                  };
                  input.click();
                }}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-semibold transition"
              >
                ➕ Upload Document
              </button>
            </div>

            <div className="bg-gray-800 rounded-xl p-6">
              <div className="text-center py-12">
                <div className="text-6xl mb-4 opacity-20">📄</div>
                <h3 className="text-xl font-bold mb-2">Document Management</h3>
                <p className="text-gray-400 mb-6">
                  Upload, organize, and track project documents. Link documents to specific projects for easy access.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                  <div className="bg-gray-700/50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">📋</div>
                    <p className="font-semibold text-sm">RFPs & Proposals</p>
                  </div>
                  <div className="bg-gray-700/50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">📊</div>
                    <p className="font-semibold text-sm">Reports & Analytics</p>
                  </div>
                  <div className="bg-gray-700/50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">📝</div>
                    <p className="font-semibold text-sm">Contracts & Agreements</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: ANALYTICS */}
        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📈 Project Analytics</h2>
              <p className="text-gray-400">Performance metrics and project insights</p>
            </div>

            {/* Real Stats from Projects */}
            {projectsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-400">Loading analytics...</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-xl">
                    <h3 className="text-sm font-semibold text-white/80 mb-2">Total Projects</h3>
                    <div className="text-4xl font-bold mb-1">{projects.length}</div>
                    <p className="text-sm text-white/70">All Time</p>
                  </div>

                  <div className="bg-gradient-to-br from-green-600 to-green-800 p-6 rounded-xl">
                    <h3 className="text-sm font-semibold text-white/80 mb-2">Active Projects</h3>
                    <div className="text-4xl font-bold mb-1">
                      {projects.filter((p: any) => p.status === 'Active' || p.status === 'In Progress').length}
                    </div>
                    <p className="text-sm text-white/70">In Progress</p>
                  </div>

                  <div className="bg-gradient-to-br from-purple-600 to-purple-800 p-6 rounded-xl">
                    <h3 className="text-sm font-semibold text-white/80 mb-2">Total Value</h3>
                    <div className="text-4xl font-bold mb-1">
                      ${(projects.reduce((sum: number, p: any) => sum + (p.budget || 0), 0) / 1000).toFixed(0)}K
                    </div>
                    <p className="text-sm text-white/70">Total Budget</p>
                  </div>

                  <div className="bg-gradient-to-br from-yellow-600 to-yellow-800 p-6 rounded-xl">
                    <h3 className="text-sm font-semibold text-white/80 mb-2">Avg Completion</h3>
                    <div className="text-4xl font-bold mb-1">
                      {projects.length > 0 
                        ? Math.round(projects.reduce((sum: number, p: any) => sum + (p.completion_percentage || 0), 0) / projects.length)
                        : 0}%
                    </div>
                    <p className="text-sm text-white/70">Average Progress</p>
                  </div>
                </div>

                {/* Project Status Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4">Project Status</h3>
                    <div className="space-y-3">
                      {[
                        { status: 'Active', count: projects.filter((p: any) => p.status === 'Active' || p.status === 'In Progress').length, color: 'green' },
                        { status: 'Planning', count: projects.filter((p: any) => p.status === 'Planning').length, color: 'yellow' },
                        { status: 'Completed', count: projects.filter((p: any) => p.status === 'Completed').length, color: 'blue' },
                        { status: 'On Hold', count: projects.filter((p: any) => p.status === 'On Hold').length, color: 'gray' }
                      ].map((item, idx) => (
                        <div key={idx} className={`bg-${item.color}-900/30 border border-${item.color}-700/50 px-4 py-3 rounded-lg`}>
                          <div className="flex justify-between items-center">
                            <span className={`font-semibold text-${item.color}-400`}>{item.status}</span>
                            <span className="text-2xl font-bold">{item.count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-800 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4">Budget Breakdown</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-400">Total Budget</span>
                          <span className="font-bold text-green-400">
                            ${projects.reduce((sum: number, p: any) => sum + (p.budget || 0), 0).toLocaleString()}
                          </span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: '100%' }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-400">Completed Budget</span>
                          <span className="font-bold text-blue-400">
                            ${projects.reduce((sum: number, p: any) => {
                              const completion = (p.completion_percentage || 0) / 100;
                              return sum + ((p.budget || 0) * completion);
                            }, 0).toLocaleString()}
                          </span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ 
                              width: `${projects.length > 0 
                                ? (projects.reduce((sum: number, p: any) => {
                                    const completion = (p.completion_percentage || 0) / 100;
                                    return sum + ((p.budget || 0) * completion);
                                  }, 0) / projects.reduce((sum: number, p: any) => sum + (p.budget || 0), 0)) * 100
                                : 0}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB: TASK BOARD */}
        {activeTab === 'task-board' && (
          <div>
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-3xl font-bold mb-2">📋 Task Board</h2>
                  <p className="text-gray-400">Monday.com-style project management with AI automation</p>
                </div>
                <button 
                  onClick={async () => {
                    const newTask: Task = {
                      id: Date.now().toString(),
                      title: 'New Task',
                      status: 'todo',
                      priority: 'medium',
                      owner: 'Unassigned',
                      dueDate: new Date().toISOString().split('T')[0],
                      progress: 0
                    };
                    setTasks([...tasks, newTask]);
                    setSelectedTask(newTask);
                    setShowTaskModal(true);
                  }}
                  className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 rounded-xl font-bold shadow-lg shadow-green-500/20 transition"
                >
                  + New Task
                </button>
              </div>

              {/* View Switcher */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setBoardView('board')}
                  className={`px-4 py-2 rounded-lg font-bold transition ${
                    boardView === 'board'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  📋 Board
                </button>
                <button
                  onClick={() => setBoardView('timeline')}
                  className={`px-4 py-2 rounded-lg font-bold transition ${
                    boardView === 'timeline'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  📅 Timeline
                </button>
                <div className="relative">
                  <button
                    onClick={() => setShowCalendarMenu(!showCalendarMenu)}
                    className="px-4 py-2 rounded-lg font-bold transition bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
                  >
                    📆 Sync Calendar
                  </button>
                  
                  {showCalendarMenu && (
                    <div className="absolute top-full mt-2 left-0 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl p-3 z-50 min-w-[280px]">
                      <div className="text-xs text-gray-400 font-bold mb-2 uppercase">macOS Calendar Integration</div>
                      <button
                        onClick={() => {
                          downloadAllTasksICS();
                          setShowCalendarMenu(false);
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-gray-700 rounded-lg transition mb-2"
                      >
                        <div className="font-semibold mb-1">📱 Export All Tasks</div>
                        <div className="text-xs text-gray-400">Download all {tasks.filter(t => t.dueDate).length} tasks to Calendar</div>
                      </button>
                      <button
                        onClick={() => {
                          const incompleteTasks = tasks.filter(t => t.status !== 'done' && t.dueDate);
                          const allEvents = incompleteTasks.map((task) => {
                            const startDate = new Date(task.dueDate);
                            const endDate = new Date(startDate.getTime() + 60 * 60 * 1000);
                            
                            const formatDate = (date: Date) => {
                              return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
                            };

                            return `BEGIN:VEVENT
UID:${task.id}@nexus.local
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(startDate)}
DTEND:${formatDate(endDate)}
SUMMARY:${task.title}
DESCRIPTION:${task.description || 'ATLAS PM Task'}
LOCATION:NEXUS - ATLAS PM
STATUS:CONFIRMED
ORGANIZER:CN=${task.owner}
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Task Due: ${task.title}
END:VALARM
END:VEVENT`;
                          }).join('\n');

                          const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//NEXUS//ATLAS PM//EN
${allEvents}
END:VCALENDAR`;

                          const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
                          const url = window.URL.createObjectURL(blob);
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = 'ATLAS_PM_Pending_Tasks.ics';
                          document.body.appendChild(link);
                          link.click();
                          document.body.removeChild(link);
                          window.URL.revokeObjectURL(url);
                          
                          setNotification({ message: `${incompleteTasks.length} pending tasks exported!`, type: 'success' });
                          setTimeout(() => setNotification(null), 3000);
                          setShowCalendarMenu(false);
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-gray-700 rounded-lg transition mb-2"
                      >
                        <div className="font-semibold mb-1">⏳ Export Pending Only</div>
                        <div className="text-xs text-gray-400">Only tasks not yet complete</div>
                      </button>
                      <div className="border-t border-gray-700 my-2"></div>
                      <div className="px-4 py-2 text-xs text-gray-500">
                        💡 Tip: Click 📅 on any task card to add it individually
                      </div>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setBoardView('list')}
                  className={`px-4 py-2 rounded-lg font-bold transition ${
                    boardView === 'list'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  📝 List
                </button>
              </div>
            </div>

            {/* AI Assistant Banner */}
            <div className="mb-6 bg-gradient-to-r from-blue-900/40 to-purple-900/40 border border-blue-500/30 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <span className="text-3xl">🤖</span>
                <div className="flex-1">
                  <h3 className="font-bold text-blue-400 mb-1">AI Assistant Active</h3>
                  <p className="text-sm text-gray-300">Monitoring {tasks.length} tasks • {tasks.filter(t => t.status === 'in-progress').length} in progress • {tasks.filter(t => t.status === 'review').length} awaiting review</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold text-sm transition">
                  View Insights
                </button>
              </div>
            </div>

            {/* BOARD VIEW - Kanban */}
            {boardView === 'board' && (
              <div className="grid grid-cols-4 gap-4">
                {['todo', 'in-progress', 'review', 'done'].map((status) => {
                  const statusTasks = tasks.filter(t => t.status === status);
                  const statusConfig = {
                    'todo': { label: '📝 To Do', color: 'bg-gray-500', count: statusTasks.length },
                    'in-progress': { label: '🔄 In Progress', color: 'bg-blue-500', count: statusTasks.length },
                    'review': { label: '👀 Review', color: 'bg-yellow-500', count: statusTasks.length },
                    'done': { label: '✅ Done', color: 'bg-green-500', count: statusTasks.length }
                  };
                  const config = statusConfig[status as keyof typeof statusConfig];

                  return (
                    <div key={status} className="bg-gray-800/40 border border-gray-700 rounded-xl p-4">
                      {/* Column Header */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 ${config.color} rounded-full`}></div>
                          <h3 className="font-bold">{config.label}</h3>
                          <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
                            {config.count}
                          </span>
                        </div>
                      </div>

                      {/* Tasks */}
                      <div className="space-y-3">
                        {statusTasks.map((task) => {
                          const priorityConfig = {
                            'urgent': { bg: 'bg-red-500/20', text: 'text-red-400', label: 'URGENT' },
                            'high': { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'HIGH' },
                            'medium': { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'MED' },
                            'low': { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'LOW' }
                          };
                          const priority = priorityConfig[task.priority];

                          return (
                            <div
                              key={task.id}
                              onClick={() => {
                                setSelectedTask(task);
                                setShowTaskModal(true);
                              }}
                              className="group relative overflow-hidden bg-gray-900 border border-gray-700 rounded-lg p-3 hover:border-blue-500 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-lg"
                            >
                              {/* Priority Badge & Actions */}
                              <div className="flex items-center justify-between mb-2">
                                <span className={`text-xs px-2 py-1 rounded-full font-bold ${priority.bg} ${priority.text}`}>
                                  {priority.label}
                                </span>
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                                  <button 
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadICS(task);
                                    }}
                                    className="text-sm hover:text-blue-400 transition"
                                    title="Add to Calendar"
                                  >
                                    📅
                                  </button>
                                  <button 
                                    onClick={async (e) => {
                                      e.stopPropagation();
                                      const statusFlow: Array<Task['status']> = ['todo', 'in-progress', 'review', 'done'];
                                      const currentIndex = statusFlow.indexOf(task.status);
                                      if (currentIndex < statusFlow.length - 1) {
                                        const newStatus = statusFlow[currentIndex + 1];
                                        const updatedTask = {...task, status: newStatus};
                                        setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
                                        await saveTask(updatedTask);
                                        setNotification({ message: 'Task moved to ' + newStatus.replace('-', ' '), type: 'success' });
                                        setTimeout(() => setNotification(null), 2000);
                                      }
                                    }}
                                    className="text-xs text-blue-400 hover:text-blue-300 font-semibold"
                                  >
                                    →
                                  </button>
                                </div>
                              </div>

                              {/* Task Title */}
                              <h4 className="font-semibold mb-2 text-sm">{task.title}</h4>

                              {/* Progress Bar */}
                              <div className="mb-3">
                                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                                  <span>Progress</span>
                                  <span>{task.progress}%</span>
                                </div>
                                <div className="w-full bg-gray-800 rounded-full h-1.5">
                                  <div
                                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full transition-all"
                                    style={{ width: `${task.progress}%` }}
                                  ></div>
                                </div>
                              </div>

                              {/* Meta Info */}
                              <div className="flex items-center justify-between text-xs">
                                <div className="flex items-center gap-1 text-gray-400">
                                  <span>👤</span>
                                  <span>{task.owner.split(' ')[0]}</span>
                                </div>
                                <div className="flex items-center gap-1 text-gray-400">
                                  <span>📅</span>
                                  <span>{new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                                </div>
                              </div>

                              {task.budget && (
                                <div className="mt-2 text-xs text-gray-500">
                                  💰 ${task.budget.toLocaleString()}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {/* Add Task Button */}
                      <button 
                        onClick={() => {
                          const newTask: Task = {
                            id: Date.now().toString(),
                            title: 'New Task',
                            status: status as Task['status'],
                            priority: 'medium',
                            owner: 'Unassigned',
                            dueDate: new Date().toISOString().split('T')[0],
                            progress: 0
                          };
                          setTasks([...tasks, newTask]);
                          setSelectedTask(newTask);
                          setShowTaskModal(true);
                        }}
                        className="w-full mt-3 py-2 border-2 border-dashed border-gray-700 hover:border-gray-600 rounded-lg text-gray-500 hover:text-gray-400 text-sm font-semibold transition"
                      >
                        + Add Task
                      </button>
                    </div>
                  );
                })}
              </div>
            )}

            {/* TIMELINE VIEW */}
            {boardView === 'timeline' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden p-8">
                <div className="text-center">
                  <div className="text-6xl mb-4">📅</div>
                  <h3 className="text-2xl font-bold mb-2">Timeline View</h3>
                  <p className="text-gray-400">Gantt chart coming soon - visualize task dependencies and timelines</p>
                </div>
              </div>
            )}

            {/* CALENDAR VIEW */}
            {boardView === 'calendar' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden p-8">
                <div className="text-center">
                  <div className="text-6xl mb-4">📆</div>
                  <h3 className="text-2xl font-bold mb-2">Calendar View</h3>
                  <p className="text-gray-400">Calendar view coming soon - see all tasks by date</p>
                </div>
              </div>
            )}

            {/* LIST VIEW */}
            {boardView === 'list' && (
              <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden p-8">
                <div className="text-center">
                  <div className="text-6xl mb-4">📝</div>
                  <h3 className="text-2xl font-bold mb-2">List View</h3>
                  <p className="text-gray-400">Spreadsheet-style list view coming soon</p>
                </div>
              </div>
            )}

            {/* Task Detail Modal */}
            {showTaskModal && selectedTask && (
              <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                <div className="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
                  {/* Modal Header */}
                  <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                    <input
                      className="text-3xl font-bold bg-transparent border-none outline-none w-full mb-3 placeholder-white/50"
                      value={selectedTask.title}
                      onChange={(e) => {
                        const updated = {...selectedTask, title: e.target.value};
                        setSelectedTask(updated);
                        setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                      }}
                      placeholder="Task title..."
                    />
                    <div className="flex gap-2">
                      <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-semibold">
                        {selectedTask.priority.toUpperCase()} Priority
                      </span>
                      <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-semibold capitalize">
                        {selectedTask.status.replace('-', ' ')}
                      </span>
                    </div>
                  </div>

                  {/* Modal Content */}
                  <div className="p-6 grid grid-cols-3 gap-6">
                    {/* Main Column */}
                    <div className="col-span-2 space-y-6">
                      {/* Description */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">DESCRIPTION</label>
                        <textarea
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 h-32 text-white resize-none focus:border-blue-500 outline-none"
                          placeholder="Add task description..."
                          value={selectedTask.description || ''}
                          onChange={(e) => {
                            const updated = {...selectedTask, description: e.target.value};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        />
                      </div>

                      {/* AI Suggestions */}
                      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                          <span className="text-xl">🤖</span>
                          <div>
                            <h4 className="font-bold text-blue-400 mb-1">AI Suggestion</h4>
                            <p className="text-sm text-gray-300">
                              {selectedTask.progress === 0 ? 
                                "Just getting started? Set a realistic first milestone to track progress." :
                                selectedTask.progress < 50 ?
                                "You're making progress! Consider breaking this into subtasks for better tracking." :
                                selectedTask.progress < 100 ?
                                "Almost there! This task is blocking 2 other tasks - consider prioritizing completion." :
                                "Great work! This task is complete. Ready to move to the next phase?"
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-4">
                      {/* Status */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">STATUS</label>
                        <select
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                          value={selectedTask.status}
                          onChange={(e) => {
                            const updated = {...selectedTask, status: e.target.value as Task['status']};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        >
                          <option value="todo">To Do</option>
                          <option value="in-progress">In Progress</option>
                          <option value="review">Review</option>
                          <option value="done">Done</option>
                        </select>
                      </div>

                      {/* Priority */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">PRIORITY</label>
                        <select
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                          value={selectedTask.priority}
                          onChange={(e) => {
                            const updated = {...selectedTask, priority: e.target.value as Task['priority']};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        >
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                          <option value="urgent">Urgent</option>
                        </select>
                      </div>

                      {/* Owner */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">OWNER</label>
                        <select
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                          value={selectedTask.owner}
                          onChange={(e) => {
                            const updated = {...selectedTask, owner: e.target.value};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        >
                          <option>Dee Davis</option>
                          <option>Mike Chen</option>
                          <option>Sarah Johnson</option>
                          <option>Unassigned</option>
                        </select>
                      </div>

                      {/* Due Date */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">DUE DATE</label>
                        <input
                          type="date"
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                          value={selectedTask.dueDate}
                          onChange={(e) => {
                            const updated = {...selectedTask, dueDate: e.target.value};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        />
                      </div>

                      {/* Progress */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">PROGRESS</label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={selectedTask.progress}
                          onChange={(e) => {
                            const updated = {...selectedTask, progress: parseInt(e.target.value)};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                          className="w-full"
                        />
                        <div className="text-center text-3xl font-bold mt-2">{selectedTask.progress}%</div>
                      </div>

                      {/* Budget */}
                      <div>
                        <label className="text-sm font-bold text-gray-400 mb-2 block">BUDGET</label>
                        <input
                          type="number"
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
                          placeholder="$5,000"
                          value={selectedTask.budget || ''}
                          onChange={(e) => {
                            const updated = {...selectedTask, budget: parseInt(e.target.value) || 0};
                            setSelectedTask(updated);
                            setTasks(tasks.map(t => t.id === selectedTask.id ? updated : t));
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Modal Footer */}
                  <div className="border-t border-gray-700 p-4 flex justify-between items-center">
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          downloadICS(selectedTask);
                        }}
                        className="px-4 py-2 bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 rounded-lg font-semibold transition flex items-center gap-2"
                      >
                        📅 Add to Calendar
                      </button>
                      <button
                        onClick={async () => {
                          if (window.confirm('Delete this task?')) {
                            await deleteTaskFromDB(selectedTask.id);
                            setTasks(tasks.filter(t => t.id !== selectedTask.id));
                            setShowTaskModal(false);
                            setNotification({ message: 'Task deleted', type: 'success' });
                            setTimeout(() => setNotification(null), 3000);
                          }
                        }}
                        className="px-4 py-2 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded-lg font-semibold transition"
                      >
                        Delete
                      </button>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setShowTaskModal(false)}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition"
                      >
                        Close
                      </button>
                      <button
                        onClick={async () => {
                          const saved = await saveTask(selectedTask);
                          if (saved) {
                            setShowTaskModal(false);
                            setNotification({ message: 'Task saved to Airtable!', type: 'success' });
                            setTimeout(() => setNotification(null), 3000);
                            loadTasks(); // Reload to get fresh data
                          } else {
                            setNotification({ message: 'Error saving task', type: 'error' });
                            setTimeout(() => setNotification(null), 3000);
                          }
                        }}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-bold transition"
                      >
                        Save Changes
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Notification Toast */}
      {notification && (
        <div className={`fixed top-6 right-6 border px-6 py-4 rounded-lg shadow-2xl max-w-md z-50 ${
          notification.type === 'success' 
            ? 'bg-gray-800 border-green-500' 
            : 'bg-gray-800 border-red-500'
        }`}>
          <p className={`font-semibold ${
            notification.type === 'success' ? 'text-green-400' : 'text-red-400'
          }`}>
            {notification.message}
          </p>
        </div>
      )}
    </div>
  );
};

export default ATLASSystem;

