import React, { useState } from 'react';

interface GPSSSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const GPSSSystem: React.FC<GPSSSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard' },
    { id: 'upload', label: '📄 Upload RFP' },
    { id: 'opportunities', label: '🎯 Opportunities' },
    { id: 'contacts', label: '👥 Contacts' },
    { id: 'products', label: '📦 Products' },
    { id: 'analytics', label: '📈 Analytics' }
  ];

  const stats = [
    { label: 'Active Opportunities', value: '1', subtext: 'Government RFPs', gradient: 'from-blue-600 to-blue-800' },
    { label: 'Total Contacts', value: '6', subtext: 'Decision Makers', gradient: 'from-green-600 to-green-800' },
    { label: 'Products', value: '5', subtext: 'Ready to Quote', gradient: 'from-purple-600 to-purple-800' },
    { label: 'Pipeline Value', value: '$15M', subtext: 'Active Contracts', gradient: 'from-yellow-600 to-yellow-800' }
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

  const extractContacts = async () => {
    if (!selectedFile) return;

    setIsExtracting(true);
    
    try {
      const response = await fetch('http://127.0.0.1:8000/extract-contacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_text: "Sample RFP content for contact extraction",
          document_name: selectedFile.name
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification(`🎉 Found ${result.contacts_found} contacts! Stored ${result.contacts_stored} in Airtable.`, 'success');
        setSelectedFile(null);
        const fileInput = document.getElementById('fileInput') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
        
        setTimeout(() => setActiveTab('contacts'), 2000);
      }
    } catch (error) {
      showNotification('❌ Error extracting contacts', 'error');
    } finally {
      setIsExtracting(false);
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
              <h2 className="text-3xl font-bold mb-2">Government Contracting Command Center</h2>
              <p className="text-gray-400">AI-powered contact extraction and opportunity management</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              {stats.map((stat, index) => (
                <div key={index} className={`bg-gradient-to-br ${stat.gradient} p-6 rounded-xl`}>
                  <h3 className="text-sm font-semibold text-white/80 mb-2">{stat.label}</h3>
                  <p className="text-4xl font-bold mb-1">{stat.value}</p>
                  <p className="text-sm text-white/70">{stat.subtext}</p>
                </div>
              ))}
            </div>

            {/* Recent Activity Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Recent Opportunities */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">🎯 Recent Opportunities</h3>
                <div className="space-y-3">
                  <div className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg hover:bg-gray-700 transition">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h4 className="font-bold text-blue-400">Wisconsin NEMT RFP</h4>
                        <p className="text-sm text-gray-400">Wisconsin Department of Health Services</p>
                      </div>
                      <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded">HIGH</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-400">RFP: WI-DHS-2026-001</span>
                      <span className="text-green-400 font-bold">$15.0M</span>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Deadline: Feb 15, 2026
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Contacts */}
              <div className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-xl font-bold mb-4">👥 Recent Contacts</h3>
                <div className="space-y-3">
                  <div className="bg-gray-700/50 border border-gray-600 px-4 py-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-bold text-purple-400">Sarah Johnson</h4>
                        <p className="text-sm text-gray-400">Contracting Officer</p>
                      </div>
                      <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded">HIGH</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">Wisconsin DHS</p>
                    <div className="flex gap-4 text-xs text-gray-500">
                      <span>📧 sarah.johnson@dhs.wisconsin.gov</span>
                    </div>
                  </div>
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">Upload an RFP to extract more contacts!</p>
                  </div>
                </div>
              </div>
            </div>

            {/* AI System Status */}
            <div className="mt-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold mb-1">🤖 AI Contact Extraction System</h3>
                  <p className="text-sm text-gray-400">Powered by Claude Sonnet 4 • Connected to Airtable</p>
                </div>
                <div className="flex items-center gap-2 bg-green-500/20 px-4 py-2 rounded-lg">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-400 font-semibold">Online & Ready</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: UPLOAD RFP */}
        {activeTab === 'upload' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📄 Upload RFP Document</h2>
              <p className="text-gray-400">AI will automatically extract all contacts with categorization</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
              <div 
                className={`border-3 border-dashed ${isDragging ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-700/30'} p-12 rounded-xl text-center cursor-pointer hover:border-blue-500 hover:bg-gray-800 transition`}
                onClick={() => document.getElementById('fileInput')?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="text-6xl mb-4">📎</div>
                <h3 className="text-xl font-bold mb-2 text-blue-400">Drop RFP PDF here or click to browse</h3>
                <p className="text-gray-400 mb-4">AI will extract: Contracting Officers, Program Managers, POCs</p>
                <input 
                  type="file" 
                  id="fileInput" 
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

              {selectedFile && !isExtracting && (
                <div className="mt-6 text-center">
                  <button 
                    onClick={extractContacts}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-lg font-bold text-lg transition"
                  >
                    🤖 Extract Contacts with AI
                  </button>
                </div>
              )}

              {isExtracting && (
                <div className="mt-6">
                  <div className="bg-blue-900/30 border border-blue-700 p-6 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <div>
                        <h4 className="font-bold text-blue-400 mb-1">AI Processing Document...</h4>
                        <p className="text-sm text-gray-400">Extracting contacts and categorizing by role</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB: OPPORTUNITIES */}
        {activeTab === 'opportunities' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">🎯 Active Opportunities</h2>
              <p className="text-gray-400">Government contracts and RFPs</p>
            </div>

            <div className="bg-gray-800 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">RFP Name</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Agency</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Value</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Deadline</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t border-gray-700 hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div className="font-bold text-blue-400">Wisconsin NEMT RFP</div>
                      <div className="text-sm text-gray-400">WI-DHS-2026-001</div>
                    </td>
                    <td className="px-6 py-4 text-gray-300">Wisconsin DHS</td>
                    <td className="px-6 py-4 text-green-400 font-bold">$15.0M</td>
                    <td className="px-6 py-4 text-gray-300">Feb 15, 2026</td>
                    <td className="px-6 py-4">
                      <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-sm font-bold">HIGH</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB: CONTACTS */}
        {activeTab === 'contacts' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">👥 All Contacts</h2>
              <p className="text-gray-400">Auto-extracted and categorized decision makers</p>
            </div>

            <div className="bg-gray-800 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Name</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Title / Role</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Organization</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Email</th>
                    <th className="text-left px-6 py-4 font-semibold text-gray-300">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t border-gray-700 hover:bg-gray-700/50">
                    <td className="px-6 py-4 font-bold text-purple-400">Sarah Johnson</td>
                    <td className="px-6 py-4">
                      <div className="text-gray-300">Contracting Officer</div>
                      <div className="text-xs text-gray-500">Decision Maker</div>
                    </td>
                    <td className="px-6 py-4 text-gray-300">Wisconsin DHS</td>
                    <td className="px-6 py-4 text-gray-400 text-sm">sarah.johnson@dhs.wisconsin.gov</td>
                    <td className="px-6 py-4">
                      <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-sm font-bold">HIGH</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB: PRODUCTS */}
        {activeTab === 'products' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📦 Product Catalog</h2>
              <p className="text-gray-400">Government-approved products ready to quote</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/50 border border-blue-700 p-6 rounded-xl">
                <div className="text-4xl mb-3">🚨</div>
                <h3 className="font-bold text-lg mb-2">Emergency Kits</h3>
                <p className="text-sm text-gray-400 mb-4">72-hour emergency supplies, first aid, trauma kits</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-blue-400">5</span>
                  <span className="text-sm text-gray-400">Products</span>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/50 border border-purple-700 p-6 rounded-xl">
                <div className="text-4xl mb-3">⚡</div>
                <h3 className="font-bold text-lg mb-2">Generators</h3>
                <p className="text-sm text-gray-400 mb-4">3kW-20kW portable and standby power systems</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-purple-400">4</span>
                  <span className="text-sm text-gray-400">Products</span>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-900/50 to-green-800/50 border border-green-700 p-6 rounded-xl">
                <div className="text-4xl mb-3">🏠</div>
                <h3 className="font-bold text-lg mb-2">Temporary Housing</h3>
                <p className="text-sm text-gray-400 mb-4">Manufactured homes, modular buildings, containers</p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-green-400">8</span>
                  <span className="text-sm text-gray-400">Products</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: ANALYTICS */}
        {activeTab === 'analytics' && (
          <div>
            <div className="mb-6">
              <h2 className="text-3xl font-bold mb-2">📈 Analytics Dashboard</h2>
              <p className="text-gray-400">Performance metrics and insights</p>
            </div>

            <div className="bg-gray-800 rounded-xl p-8 text-center">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-2xl font-bold mb-2">Analytics Coming Soon</h3>
              <p className="text-gray-400">Track win rates, contact quality, and pipeline velocity</p>
            </div>
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

export default GPSSSystem;
