import React, { useState, useEffect } from 'react';
import { Power, PlayCircle, StopCircle, RefreshCw, CheckCircle, XCircle, Clock, Mail, Calendar, AlertTriangle } from 'lucide-react';

interface SystemStatus {
  automation_running: boolean;
  cron_jobs_count: number;
  last_notification_check: string;
  next_notification_check: string;
  emails_sent_today: number;
  urgent_bids_count: number;
  backend_running: boolean;
  frontend_running: boolean;
}

export const SystemControlPanel: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [testingEmail, setTestingEmail] = useState(false);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system-status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    } finally {
      setLoading(false);
    }
  };

  const testNotifications = async () => {
    setTestingEmail(true);
    try {
      const response = await fetch('http://localhost:8000/api/test-notification', {
        method: 'POST'
      });
      if (response.ok) {
        alert('✅ Test notification sent! Check bids.deedavisinc@gmail.com');
      } else {
        alert('❌ Failed to send test notification');
      }
    } catch (error) {
      alert('❌ Error: ' + error);
    } finally {
      setTestingEmail(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading system status...</span>
        </div>
      </div>
    );
  }

  const allSystemsRunning = status?.backend_running && status?.automation_running;

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Power className={`w-6 h-6 ${allSystemsRunning ? 'text-green-400' : 'text-red-400'}`} />
          <div>
            <h2 className="text-xl font-bold text-white">NEXUS System Control</h2>
            <p className="text-sm text-gray-400">Real-time status and controls</p>
          </div>
        </div>
        
        <div className={`px-4 py-2 rounded-lg font-semibold ${
          allSystemsRunning 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-red-500/20 text-red-400'
        }`}>
          {allSystemsRunning ? '✅ RUNNING' : '❌ OFFLINE'}
        </div>
      </div>

      {/* System Components Status */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <StatusCard
          title="Backend API"
          status={status?.backend_running || false}
          icon={<Power className="w-5 h-5" />}
          details="Port 8000"
        />
        <StatusCard
          title="Automation Engine"
          status={status?.automation_running || false}
          icon={<RefreshCw className="w-5 h-5" />}
          details={`${status?.cron_jobs_count || 0} cron jobs`}
        />
        <StatusCard
          title="Email Notifications"
          status={status?.automation_running || false}
          icon={<Mail className="w-5 h-5" />}
          details={`${status?.emails_sent_today || 0} sent today`}
        />
        <StatusCard
          title="Urgent Bids"
          status={(status?.urgent_bids_count || 0) > 0}
          icon={<AlertTriangle className="w-5 h-5" />}
          details={`${status?.urgent_bids_count || 0} urgent (≤ 3 days)`}
          warning={(status?.urgent_bids_count || 0) > 0}
        />
      </div>

      {/* Automation Schedule */}
      <div className="bg-gray-750 rounded-lg p-4 mb-6">
        <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Notification Schedule (Automatic)
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Last Check:</span>
            <span className="text-white">{status?.last_notification_check || 'Never'}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Next Check:</span>
            <span className="text-green-400">{status?.next_notification_check || 'Unknown'}</span>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="text-gray-400 text-xs space-y-1">
              <div>• Daily: 7 AM, 12 PM, 6 PM</div>
              <div>• Critical: Every 2 hours (6 AM - 8 PM)</div>
              <div>• Emails: ONLY for bids ≤ 3 days away</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-3">
        <button
          onClick={testNotifications}
          disabled={testingEmail || !status?.backend_running}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
        >
          {testingEmail ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Mail className="w-5 h-5" />
              Test Notification Email
            </>
          )}
        </button>
        
        <button
          onClick={fetchStatus}
          className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
        >
          <RefreshCw className="w-5 h-5" />
          Refresh
        </button>
      </div>

      {/* Warning if system offline */}
      {!allSystemsRunning && (
        <div className="mt-4 bg-red-500/20 border border-red-500 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-red-400 font-semibold mb-1">System Not Running</div>
              <div className="text-sm text-gray-300">
                To start NEXUS automation, run: <code className="bg-gray-900 px-2 py-1 rounded">./START_NEXUS_WITH_NOTIFICATIONS.sh</code>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface StatusCardProps {
  title: string;
  status: boolean;
  icon: React.ReactNode;
  details: string;
  warning?: boolean;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, status, icon, details, warning }) => {
  return (
    <div className={`bg-gray-750 rounded-lg p-4 border-l-4 ${
      warning 
        ? 'border-yellow-500' 
        : status 
          ? 'border-green-500' 
          : 'border-red-500'
    }`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={warning ? 'text-yellow-400' : status ? 'text-green-400' : 'text-red-400'}>
            {icon}
          </div>
          <span className="text-white font-medium text-sm">{title}</span>
        </div>
        {status ? (
          <CheckCircle className="w-4 h-4 text-green-400" />
        ) : (
          <XCircle className="w-4 h-4 text-red-400" />
        )}
      </div>
      <div className="text-xs text-gray-400 ml-7">{details}</div>
    </div>
  );
};

export default SystemControlPanel;
