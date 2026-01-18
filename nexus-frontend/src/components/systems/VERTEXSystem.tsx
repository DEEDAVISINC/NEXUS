import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface VERTEXSystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const VERTEXSystem: React.FC<VERTEXSystemProps> = ({ onBackToNexus, activeTab, setActiveTab }) => {
  // Dashboard state
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Invoices state
  const [invoices, setInvoices] = useState<any[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [invoiceFilters, setInvoiceFilters] = useState({
    payment_status: 'all',
    source_system: 'all'
  });

  // Expenses state
  const [expenses, setExpenses] = useState<any[]>([]);
  const [showExpenseModal, setShowExpenseModal] = useState(false);
  const [expenseFormData, setExpenseFormData] = useState({
    expense_date: new Date().toISOString().split('T')[0],
    vendor: '',
    description: '',
    category: 'Other',
    amount: 0,
    payment_method: 'Credit Card',
    payment_status: 'Paid',
    tax_deductible: true,
    billable: false
  });

  // Revenue state
  const [revenueRecords, setRevenueRecords] = useState<any[]>([]);
  const [revenueSummary, setRevenueSummary] = useState<any>(null);

  // Reports state
  const [profitLossData, setProfitLossData] = useState<any>(null);
  const [financialHealthScore, setFinancialHealthScore] = useState<any>(null);

  // Notification state
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Load dashboard data on mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Load data when tab changes
  useEffect(() => {
    if (activeTab === 'invoices') fetchInvoices();
    else if (activeTab === 'expenses') fetchExpenses();
    else if (activeTab === 'revenue') fetchRevenue();
    else if (activeTab === 'reports') fetchReports();
  }, [activeTab, invoiceFilters]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await api.getVertexDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching VERTEX dashboard:', error);
      showNotification('Error loading dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoices = async () => {
    try {
      const filters = invoiceFilters.payment_status !== 'all' || invoiceFilters.source_system !== 'all' 
        ? { 
            payment_status: invoiceFilters.payment_status !== 'all' ? invoiceFilters.payment_status : undefined,
            source_system: invoiceFilters.source_system !== 'all' ? invoiceFilters.source_system : undefined
          }
        : undefined;
      
      const response = await api.getVertexInvoices(filters);
      setInvoices(response.invoices || []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      setInvoices([]);
    }
  };

  const fetchExpenses = async () => {
    try {
      const response = await api.getVertexExpenses();
      setExpenses(response.expenses || []);
    } catch (error) {
      console.error('Error fetching expenses:', error);
      setExpenses([]);
    }
  };

  const fetchRevenue = async () => {
    try {
      const [records, summary] = await Promise.all([
        api.getVertexRevenue(),
        api.getRevenueSummary()
      ]);
      setRevenueRecords(records.revenue || []);
      setRevenueSummary(summary);
    } catch (error) {
      console.error('Error fetching revenue:', error);
      setRevenueRecords([]);
    }
  };

  const fetchReports = async () => {
    try {
      const [pl, health] = await Promise.all([
        api.getProfitLossStatement(),
        api.getFinancialHealthScore()
      ]);
      setProfitLossData(pl);
      setFinancialHealthScore(health);
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const createExpense = async () => {
    try {
      await api.createVertexExpense(expenseFormData);
      showNotification('✅ Expense created successfully!');
      setShowExpenseModal(false);
      fetchExpenses();
      fetchDashboardData(); // Refresh dashboard
      // Reset form
      setExpenseFormData({
        expense_date: new Date().toISOString().split('T')[0],
        vendor: '',
        description: '',
        category: 'Other',
        amount: 0,
        payment_method: 'Credit Card',
        payment_status: 'Paid',
        tax_deductible: true,
        billable: false
      });
    } catch (error) {
      showNotification('❌ Error creating expense', 'error');
    }
  };

  const exportToQuickBooks = async () => {
    try {
      const result = await api.exportToQuickBooks({});
      showNotification(`✅ Exported ${result.record_count} records to QuickBooks format`);
      
      // Download CSV
      const csvContent = convertToCSV(result.data);
      downloadFile(csvContent, 'quickbooks_export.csv', 'text/csv');
    } catch (error) {
      showNotification('❌ Error exporting to QuickBooks', 'error');
    }
  };

  const convertToCSV = (data: any[]) => {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
    ];
    
    return csvRows.join('\n');
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  // ========== DASHBOARD TAB ==========
  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            💎 VERTEX Dashboard
          </h2>
          <p className="text-gray-400 mt-1">Financial Command Center</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={exportToQuickBooks}
            className="px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 rounded-lg hover:from-green-500 hover:to-green-600 transition-all"
          >
            📊 Export to QuickBooks
          </button>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500"></div>
        </div>
      ) : dashboardData ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total Revenue */}
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Total Revenue</span>
                <span className="text-2xl">💰</span>
              </div>
              <div className="text-3xl font-bold text-white">
                {formatCurrency(dashboardData.total_revenue || 0)}
              </div>
              <div className="text-sm text-green-400 mt-1">All Systems Combined</div>
            </div>

            {/* Total Expenses */}
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-red-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Total Expenses</span>
                <span className="text-2xl">💳</span>
              </div>
              <div className="text-3xl font-bold text-white">
                {formatCurrency(dashboardData.total_expenses || 0)}
              </div>
              <div className="text-sm text-red-400 mt-1">All Categories</div>
            </div>

            {/* Net Income */}
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-green-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Net Income</span>
                <span className="text-2xl">📈</span>
              </div>
              <div className="text-3xl font-bold text-white">
                {formatCurrency(dashboardData.net_income || 0)}
              </div>
              <div className="text-sm text-green-400 mt-1">
                {dashboardData.profit_margin?.toFixed(1)}% Margin
              </div>
            </div>

            {/* Accounts Receivable */}
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-yellow-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">A/R Outstanding</span>
                <span className="text-2xl">⚠️</span>
              </div>
              <div className="text-3xl font-bold text-white">
                {formatCurrency(dashboardData.accounts_receivable || 0)}
              </div>
              <div className="text-sm text-yellow-400 mt-1">
                {dashboardData.unpaid_invoice_count || 0} Unpaid Invoices
              </div>
            </div>
          </div>

          {/* Revenue by System */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20">
            <h3 className="text-xl font-bold mb-4 text-white">Revenue by System</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(dashboardData.revenue_by_system || {}).map(([system, amount]: [string, any]) => (
                <div key={system} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">{system}</div>
                  <div className="text-xl font-bold text-white">{formatCurrency(amount)}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Cash Flow Forecast */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-blue-500/20">
            <h3 className="text-xl font-bold mb-4 text-white">💵 Cash Flow Forecast</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Current Cash</div>
                <div className="text-xl font-bold text-white">
                  {formatCurrency(dashboardData.cash_flow_forecast?.current_cash || 0)}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">30 Days</div>
                <div className="text-xl font-bold text-white">
                  {formatCurrency(dashboardData.cash_flow_forecast?.projected_30_days || 0)}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">60 Days</div>
                <div className="text-xl font-bold text-white">
                  {formatCurrency(dashboardData.cash_flow_forecast?.projected_60_days || 0)}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">90 Days</div>
                <div className="text-xl font-bold text-white">
                  {formatCurrency(dashboardData.cash_flow_forecast?.projected_90_days || 0)}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20">
            <h3 className="text-xl font-bold mb-4 text-white">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button
                onClick={() => { setActiveTab('invoices'); setShowInvoiceModal(true); }}
                className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg p-4 hover:from-purple-500 hover:to-pink-500 transition-all"
              >
                <div className="text-2xl mb-2">📄</div>
                <div className="font-bold">Create Invoice</div>
              </button>
              <button
                onClick={() => { setActiveTab('expenses'); setShowExpenseModal(true); }}
                className="bg-gradient-to-r from-red-600 to-orange-600 rounded-lg p-4 hover:from-red-500 hover:to-orange-500 transition-all"
              >
                <div className="text-2xl mb-2">💳</div>
                <div className="font-bold">Record Expense</div>
              </button>
              <button
                onClick={() => setActiveTab('reports')}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg p-4 hover:from-blue-500 hover:to-cyan-500 transition-all"
              >
                <div className="text-2xl mb-2">📊</div>
                <div className="font-bold">View Reports</div>
              </button>
              <button
                onClick={exportToQuickBooks}
                className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg p-4 hover:from-green-500 hover:to-teal-500 transition-all"
              >
                <div className="text-2xl mb-2">📤</div>
                <div className="font-bold">Export Data</div>
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-gray-800 rounded-xl p-8 text-center border border-gray-700">
          <p className="text-gray-400">No dashboard data available</p>
        </div>
      )}
    </div>
  );

  // ========== INVOICES TAB ==========
  const renderInvoices = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">📄 Invoices</h2>
        <button
          onClick={() => setShowInvoiceModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all"
        >
          + New Invoice
        </button>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex gap-4 flex-wrap">
          <select
            value={invoiceFilters.payment_status}
            onChange={(e) => setInvoiceFilters({ ...invoiceFilters, payment_status: e.target.value })}
            className="bg-gray-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="all">All Payment Status</option>
            <option value="Unpaid">Unpaid</option>
            <option value="Partial">Partial</option>
            <option value="Paid">Paid</option>
            <option value="Overdue">Overdue</option>
            <option value="Factored">Factored</option>
          </select>

          <select
            value={invoiceFilters.source_system}
            onChange={(e) => setInvoiceFilters({ ...invoiceFilters, source_system: e.target.value })}
            className="bg-gray-700 rounded-lg px-4 py-2 text-white"
          >
            <option value="all">All Systems</option>
            <option value="GPSS">GPSS</option>
            <option value="ATLAS">ATLAS</option>
            <option value="DDCSS">DDCSS</option>
            <option value="LBPC">LBPC</option>
            <option value="GBIS">GBIS</option>
          </select>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Invoice #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Client</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">System</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {invoices.map((invoice) => {
                const fields = invoice.fields || {};
                return (
                  <tr key={invoice.id} className="hover:bg-gray-700/50 cursor-pointer">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {fields['Invoice Number'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {fields['Client Name'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Invoice Date'] ? new Date(fields['Invoice Date']).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-bold">
                      {formatCurrency(fields['Total Amount'] || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        fields['Payment Status'] === 'Paid' ? 'bg-green-500/20 text-green-400' :
                        fields['Payment Status'] === 'Overdue' ? 'bg-red-500/20 text-red-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {fields['Payment Status'] || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Source System'] || 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {invoices.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No invoices found
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // ========== EXPENSES TAB ==========
  const renderExpenses = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">💳 Expenses</h2>
        <button
          onClick={() => setShowExpenseModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-red-600 to-orange-600 rounded-lg hover:from-red-500 hover:to-orange-500 transition-all"
        >
          + New Expense
        </button>
      </div>

      {/* Expenses Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Vendor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {expenses.map((expense) => {
                const fields = expense.fields || {};
                return (
                  <tr key={expense.id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Expense Date'] ? new Date(fields['Expense Date']).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {fields['Vendor/Payee'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">
                      {fields['Description'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Category'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-bold">
                      {formatCurrency(fields['Amount'] || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        fields['Payment Status'] === 'Paid' ? 'bg-green-500/20 text-green-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {fields['Payment Status'] || 'Unknown'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {expenses.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No expenses found
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // ========== REVENUE TAB ==========
  const renderRevenue = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">💵 Revenue</h2>

      {/* Revenue Summary */}
      {revenueSummary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-green-500/20">
            <div className="text-sm text-gray-400 mb-2">Total Revenue</div>
            <div className="text-3xl font-bold text-white">
              {formatCurrency(revenueSummary.total_revenue || 0)}
            </div>
          </div>
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-blue-500/20">
            <div className="text-sm text-gray-400 mb-2">Revenue Records</div>
            <div className="text-3xl font-bold text-white">
              {revenueSummary.record_count || 0}
            </div>
          </div>
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20">
            <div className="text-sm text-gray-400 mb-2">By System</div>
            <div className="space-y-1">
              {Object.entries(revenueSummary.by_system || {}).map(([system, amount]: [string, any]) => (
                <div key={system} className="flex justify-between text-sm">
                  <span className="text-gray-400">{system}:</span>
                  <span className="text-white font-bold">{formatCurrency(amount)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Revenue Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">System</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {revenueRecords.map((record) => {
                const fields = record.fields || {};
                return (
                  <tr key={record.id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Revenue Date'] ? new Date(fields['Revenue Date']).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {fields['Source'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Revenue Type'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {fields['Source System'] || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-bold">
                      {formatCurrency(fields['Amount'] || 0)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {revenueRecords.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No revenue records found
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // ========== REPORTS TAB ==========
  const renderReports = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">📊 Financial Reports</h2>

      {/* Financial Health Score */}
      {financialHealthScore && (
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-xl font-bold mb-4 text-white">💎 Financial Health Score</h3>
          <div className="flex items-center gap-8">
            <div className="text-center">
              <div className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {financialHealthScore.overall_score?.toFixed(0) || 0}
              </div>
              <div className="text-sm text-gray-400 mt-2">Overall Score</div>
            </div>
            <div className="flex-1 grid grid-cols-3 gap-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Cash Flow</div>
                <div className="text-2xl font-bold text-white">
                  {financialHealthScore.component_scores?.cash_flow?.toFixed(0) || 0}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">A/R Management</div>
                <div className="text-2xl font-bold text-white">
                  {financialHealthScore.component_scores?.ar_management?.toFixed(0) || 0}
                </div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Profitability</div>
                <div className="text-2xl font-bold text-white">
                  {financialHealthScore.component_scores?.profitability?.toFixed(0) || 0}
                </div>
              </div>
            </div>
          </div>
          {financialHealthScore.ai_insights && (
            <div className="mt-6 bg-gray-700/30 rounded-lg p-4">
              <div className="text-sm text-gray-300 whitespace-pre-wrap">
                {financialHealthScore.ai_insights}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Profit & Loss Statement */}
      {profitLossData && (
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-green-500/20">
          <h3 className="text-xl font-bold mb-4 text-white">📈 Profit & Loss Statement</h3>
          <div className="space-y-6">
            {/* Revenue Section */}
            <div>
              <div className="text-lg font-bold text-green-400 mb-2">Revenue</div>
              {Object.entries(profitLossData.revenue?.by_system || {}).map(([system, amount]: [string, any]) => (
                <div key={system} className="flex justify-between text-gray-300 py-1">
                  <span className="pl-4">{system}:</span>
                  <span className="font-mono">{formatCurrency(amount)}</span>
                </div>
              ))}
              <div className="flex justify-between font-bold text-white mt-2 pt-2 border-t border-gray-700">
                <span>Total Revenue:</span>
                <span className="font-mono">{formatCurrency(profitLossData.revenue?.total || 0)}</span>
              </div>
            </div>

            {/* Expenses Section */}
            <div>
              <div className="text-lg font-bold text-red-400 mb-2">Expenses</div>
              {Object.entries(profitLossData.expenses?.by_category || {}).map(([category, amount]: [string, any]) => (
                <div key={category} className="flex justify-between text-gray-300 py-1">
                  <span className="pl-4">{category}:</span>
                  <span className="font-mono">{formatCurrency(amount)}</span>
                </div>
              ))}
              <div className="flex justify-between font-bold text-white mt-2 pt-2 border-t border-gray-700">
                <span>Total Expenses:</span>
                <span className="font-mono">{formatCurrency(profitLossData.expenses?.total || 0)}</span>
              </div>
            </div>

            {/* Net Income */}
            <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-lg p-4 border border-purple-500/30">
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-lg font-bold text-white">Net Income</div>
                  <div className="text-sm text-gray-400">
                    {profitLossData.profit_margin?.toFixed(1)}% Profit Margin
                  </div>
                </div>
                <div className="text-3xl font-bold text-white font-mono">
                  {formatCurrency(profitLossData.net_income || 0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // ========== EXPENSE MODAL ==========
  const renderExpenseModal = () => {
    if (!showExpenseModal) return null;

    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-2xl font-bold text-white">New Expense</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Expense Date</label>
                <input
                  type="date"
                  value={expenseFormData.expense_date}
                  onChange={(e) => setExpenseFormData({...expenseFormData, expense_date: e.target.value})}
                  className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Amount</label>
                <input
                  type="number"
                  value={expenseFormData.amount}
                  onChange={(e) => setExpenseFormData({...expenseFormData, amount: parseFloat(e.target.value) || 0})}
                  className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Vendor/Payee</label>
              <input
                type="text"
                value={expenseFormData.vendor}
                onChange={(e) => setExpenseFormData({...expenseFormData, vendor: e.target.value})}
                className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                placeholder="Who did you pay?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                value={expenseFormData.description}
                onChange={(e) => setExpenseFormData({...expenseFormData, description: e.target.value})}
                className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                rows={3}
                placeholder="What was this expense for?"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <select
                  value={expenseFormData.category}
                  onChange={(e) => setExpenseFormData({...expenseFormData, category: e.target.value})}
                  className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                >
                  <option value="Payroll">Payroll</option>
                  <option value="Software/Tools">Software/Tools</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Office Supplies">Office Supplies</option>
                  <option value="Travel">Travel</option>
                  <option value="Meals">Meals</option>
                  <option value="Equipment">Equipment</option>
                  <option value="Rent/Utilities">Rent/Utilities</option>
                  <option value="Professional Services">Professional Services</option>
                  <option value="Insurance">Insurance</option>
                  <option value="Taxes">Taxes</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Payment Method</label>
                <select
                  value={expenseFormData.payment_method}
                  onChange={(e) => setExpenseFormData({...expenseFormData, payment_method: e.target.value})}
                  className="w-full bg-gray-700 rounded-lg px-4 py-2 text-white"
                >
                  <option value="Credit Card">Credit Card</option>
                  <option value="Check">Check</option>
                  <option value="ACH">ACH</option>
                  <option value="Wire">Wire</option>
                  <option value="Cash">Cash</option>
                  <option value="Debit Card">Debit Card</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={expenseFormData.tax_deductible}
                  onChange={(e) => setExpenseFormData({...expenseFormData, tax_deductible: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-300">Tax Deductible</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={expenseFormData.billable}
                  onChange={(e) => setExpenseFormData({...expenseFormData, billable: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm text-gray-300">Billable to Client</span>
              </label>
            </div>
          </div>
          <div className="p-6 border-t border-gray-700 flex justify-end gap-3">
            <button
              onClick={() => setShowExpenseModal(false)}
              className="px-6 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={createExpense}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all"
            >
              Create Expense
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 p-8">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white`}>
          {notification.message}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="mb-8 flex gap-4 overflow-x-auto">
        {['dashboard', 'invoices', 'expenses', 'revenue', 'reports'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === tab
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab === 'dashboard' && '💎 Dashboard'}
            {tab === 'invoices' && '📄 Invoices'}
            {tab === 'expenses' && '💳 Expenses'}
            {tab === 'revenue' && '💵 Revenue'}
            {tab === 'reports' && '📊 Reports'}
          </button>
        ))}
        <button
          onClick={onBackToNexus}
          className="px-6 py-3 bg-gray-800 text-gray-400 rounded-lg hover:bg-gray-700 transition-all whitespace-nowrap ml-auto"
        >
          ← Back to NEXUS
        </button>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'invoices' && renderInvoices()}
        {activeTab === 'expenses' && renderExpenses()}
        {activeTab === 'revenue' && renderRevenue()}
        {activeTab === 'reports' && renderReports()}
      </div>

      {/* Modals */}
      {renderExpenseModal()}
    </div>
  );
};

export default VERTEXSystem;
