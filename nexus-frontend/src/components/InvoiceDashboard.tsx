import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface Invoice {
  id: string;
  'Invoice Number': string;
  'Invoice Date': string;
  'Due Date': string;
  'Invoice Status': string;
  'Client Name': string;
  'Client Type': string;
  'Source System': string;
  'Subtotal': number;
  'Shipping & Handling': number;
  'Tax Amount': number;
  'Total Amount': number;
  'Line Items': string;
  'Contract Number'?: string;
  'Purchase Order Number'?: string;
  'Payment Date'?: string;
  'Days Outstanding'?: number;
  'Sent To Email'?: string;
  'Sent Date'?: string;
  'Invoice Notes'?: string;
}

export function InvoiceDashboard() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [filteredInvoices, setFilteredInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [clientTypeFilter, setClientTypeFilter] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [showSendModal, setShowSendModal] = useState(false);
  const [sendEmail, setSendEmail] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadInvoices();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [statusFilter, sourceFilter, clientTypeFilter, invoices]);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const response = await api.getInvoices();
      if (response.success) {
        setInvoices(response.invoices || []);
      }
    } catch (error) {
      console.error('Error loading invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...invoices];

    if (statusFilter) {
      filtered = filtered.filter(inv => inv['Invoice Status'] === statusFilter);
    }
    if (sourceFilter) {
      filtered = filtered.filter(inv => inv['Source System'] === sourceFilter);
    }
    if (clientTypeFilter) {
      filtered = filtered.filter(inv => inv['Client Type'] === clientTypeFilter);
    }

    setFilteredInvoices(filtered);
  };

  const handleGenerateInvoice = async (type: 'opportunity' | 'project' | 'prospect', id: string) => {
    try {
      setIsGenerating(true);
      let response;
      
      if (type === 'opportunity') {
        response = await api.generateInvoiceFromOpportunity(id);
      } else if (type === 'project') {
        response = await api.generateInvoiceFromProject(id);
      } else {
        response = await api.generateInvoiceFromProspect(id);
      }

      if (response.success) {
        alert(`✅ Invoice ${response.invoice_number} generated successfully!`);
        loadInvoices();
      } else {
        alert(`❌ Error: ${response.message || response.error}`);
      }
    } catch (error) {
      console.error('Error generating invoice:', error);
      alert('❌ Failed to generate invoice');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendInvoice = async () => {
    if (!selectedInvoice || !sendEmail) return;

    try {
      const response = await api.sendInvoice(selectedInvoice.id, sendEmail);
      if (response.success) {
        alert(`✅ Invoice sent to ${sendEmail}!`);
        setShowSendModal(false);
        setSendEmail('');
        loadInvoices();
      } else {
        alert(`❌ Error: ${response.message || response.error}`);
      }
    } catch (error) {
      console.error('Error sending invoice:', error);
      alert('❌ Failed to send invoice');
    }
  };

  const handleDeleteInvoice = async (invoiceId: string) => {
    if (!window.confirm('Are you sure you want to delete this invoice?')) return;

    try {
      const response = await api.deleteInvoice(invoiceId);
      if (response.success) {
        alert('✅ Invoice deleted successfully!');
        loadInvoices();
        setShowInvoiceModal(false);
      } else {
        alert(`❌ Error: ${response.message || response.error}`);
      }
    } catch (error) {
      console.error('Error deleting invoice:', error);
      alert('❌ Failed to delete invoice');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Draft': return 'bg-gray-100 text-gray-800';
      case 'Sent': return 'bg-blue-100 text-blue-800';
      case 'Pending': return 'bg-yellow-100 text-yellow-800';
      case 'Paid': return 'bg-green-100 text-green-800';
      case 'Overdue': return 'bg-red-100 text-red-800';
      case 'Cancelled': return 'bg-gray-100 text-gray-500';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const stats = {
    total: invoices.length,
    draft: invoices.filter(inv => inv['Invoice Status'] === 'Draft').length,
    sent: invoices.filter(inv => inv['Invoice Status'] === 'Sent').length,
    pending: invoices.filter(inv => inv['Invoice Status'] === 'Pending').length,
    paid: invoices.filter(inv => inv['Invoice Status'] === 'Paid').length,
    overdue: invoices.filter(inv => inv['Invoice Status'] === 'Overdue').length,
    totalRevenue: invoices
      .filter(inv => inv['Invoice Status'] === 'Paid')
      .reduce((sum, inv) => sum + (inv['Total Amount'] || 0), 0),
    pendingRevenue: invoices
      .filter(inv => ['Sent', 'Pending'].includes(inv['Invoice Status']))
      .reduce((sum, inv) => sum + (inv['Total Amount'] || 0), 0),
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">💰 Invoice Dashboard</h1>
        <p className="text-gray-600">Manage government & enterprise invoices across all systems</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-600 mb-1">Total Invoices</div>
          <div className="text-3xl font-bold">{stats.total}</div>
        </div>
        <div className="bg-green-50 p-6 rounded-lg shadow">
          <div className="text-sm text-green-700 mb-1">Paid Revenue</div>
          <div className="text-3xl font-bold text-green-700">{formatCurrency(stats.totalRevenue)}</div>
          <div className="text-sm text-green-600 mt-1">{stats.paid} invoices</div>
        </div>
        <div className="bg-yellow-50 p-6 rounded-lg shadow">
          <div className="text-sm text-yellow-700 mb-1">Pending Revenue</div>
          <div className="text-3xl font-bold text-yellow-700">{formatCurrency(stats.pendingRevenue)}</div>
          <div className="text-sm text-yellow-600 mt-1">{stats.sent + stats.pending} invoices</div>
        </div>
        <div className="bg-red-50 p-6 rounded-lg shadow">
          <div className="text-sm text-red-700 mb-1">Overdue</div>
          <div className="text-3xl font-bold text-red-700">{stats.overdue}</div>
          <div className="text-sm text-red-600 mt-1">Need attention</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Sent">Sent</option>
              <option value="Pending">Pending</option>
              <option value="Paid">Paid</option>
              <option value="Overdue">Overdue</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Source System</label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All Systems</option>
              <option value="GPSS">GPSS</option>
              <option value="ATLAS">ATLAS</option>
              <option value="DDCSS">DDCSS</option>
              <option value="Manual">Manual</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Client Type</label>
            <select
              value={clientTypeFilter}
              onChange={(e) => setClientTypeFilter(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="">All Clients</option>
              <option value="Government - Federal">Government - Federal</option>
              <option value="Government - State">Government - State</option>
              <option value="Government - Local">Government - Local</option>
              <option value="Enterprise - Private">Enterprise - Private</option>
              <option value="Small Business">Small Business</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setStatusFilter('');
                setSourceFilter('');
                setClientTypeFilter('');
              }}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    Loading invoices...
                  </td>
                </tr>
              ) : filteredInvoices.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No invoices found. Generate your first invoice from GPSS, ATLAS, or DDCSS!
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                      {invoice['Invoice Number']}
                    </div>
                    {(invoice['Days Outstanding'] || 0) > 30 && invoice['Invoice Status'] !== 'Paid' && (
                      <div className="text-xs text-red-600">
                        {invoice['Days Outstanding']} days old
                      </div>
                    )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{invoice['Client Name']}</div>
                      <div className="text-xs text-gray-500">{invoice['Client Type']}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(invoice['Invoice Date'])}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(invoice['Total Amount'])}
                      </div>
                      <div className="text-xs text-gray-500">
                        Due: {formatDate(invoice['Due Date'])}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(invoice['Invoice Status'])}`}>
                        {invoice['Invoice Status']}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {invoice['Source System']}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => {
                          setSelectedInvoice(invoice);
                          setShowInvoiceModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View
                      </button>
                      {invoice['Invoice Status'] === 'Draft' && (
                        <button
                          onClick={() => {
                            setSelectedInvoice(invoice);
                            setShowSendModal(true);
                          }}
                          className="text-green-600 hover:text-green-900"
                        >
                          Send
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invoice Details Modal */}
      {showInvoiceModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold mb-1">{selectedInvoice['Invoice Number']}</h2>
                  <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${getStatusColor(selectedInvoice['Invoice Status'])}`}>
                    {selectedInvoice['Invoice Status']}
                  </span>
                </div>
                <button
                  onClick={() => setShowInvoiceModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              {/* Invoice Details */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-2">Client Information</h3>
                  <p className="text-sm"><strong>Name:</strong> {selectedInvoice['Client Name']}</p>
                  <p className="text-sm"><strong>Type:</strong> {selectedInvoice['Client Type']}</p>
                  {selectedInvoice['Contract Number'] && (
                    <p className="text-sm"><strong>Contract:</strong> {selectedInvoice['Contract Number']}</p>
                  )}
                  {selectedInvoice['Purchase Order Number'] && (
                    <p className="text-sm"><strong>PO:</strong> {selectedInvoice['Purchase Order Number']}</p>
                  )}
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Invoice Details</h3>
                  <p className="text-sm"><strong>Date:</strong> {formatDate(selectedInvoice['Invoice Date'])}</p>
                  <p className="text-sm"><strong>Due:</strong> {formatDate(selectedInvoice['Due Date'])}</p>
                  <p className="text-sm"><strong>Source:</strong> {selectedInvoice['Source System']}</p>
                  {selectedInvoice['Days Outstanding'] && (
                    <p className="text-sm"><strong>Days Out:</strong> {selectedInvoice['Days Outstanding']}</p>
                  )}
                </div>
              </div>

              {/* Line Items */}
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Line Items</h3>
                <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-line">
                  {selectedInvoice['Line Items'] || 'No line items'}
                </div>
              </div>

              {/* Amounts */}
              <div className="bg-gray-50 p-4 rounded mb-6">
                <div className="flex justify-between mb-2">
                  <span>Subtotal:</span>
                  <span className="font-semibold">{formatCurrency(selectedInvoice['Subtotal'])}</span>
                </div>
                {selectedInvoice['Shipping & Handling'] > 0 && (
                  <div className="flex justify-between mb-2">
                    <span>Shipping & Handling:</span>
                    <span className="font-semibold">{formatCurrency(selectedInvoice['Shipping & Handling'])}</span>
                  </div>
                )}
                {selectedInvoice['Tax Amount'] > 0 && (
                  <div className="flex justify-between mb-2">
                    <span>Tax:</span>
                    <span className="font-semibold">{formatCurrency(selectedInvoice['Tax Amount'])}</span>
                  </div>
                )}
                <div className="flex justify-between pt-2 border-t border-gray-300 text-lg">
                  <span className="font-bold">Total:</span>
                  <span className="font-bold">{formatCurrency(selectedInvoice['Total Amount'])}</span>
                </div>
              </div>

              {/* Notes */}
              {selectedInvoice['Invoice Notes'] && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Notes</h3>
                  <p className="text-sm text-gray-700">{selectedInvoice['Invoice Notes']}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                {selectedInvoice['Invoice Status'] === 'Draft' && (
                  <button
                    onClick={() => {
                      setShowInvoiceModal(false);
                      setShowSendModal(true);
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    📧 Send Invoice
                  </button>
                )}
                <button
                  onClick={() => handleDeleteInvoice(selectedInvoice.id)}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  🗑️ Delete
                </button>
                <button
                  onClick={() => setShowInvoiceModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Send Invoice Modal */}
      {showSendModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4">Send Invoice</h2>
            <p className="text-sm text-gray-600 mb-4">
              Send {selectedInvoice['Invoice Number']} to {selectedInvoice['Client Name']}
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Client Email
              </label>
              <input
                type="email"
                value={sendEmail}
                onChange={(e) => setSendEmail(e.target.value)}
                placeholder="client@example.com"
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleSendInvoice}
                disabled={!sendEmail}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                📧 Send Now
              </button>
              <button
                onClick={() => {
                  setShowSendModal(false);
                  setSendEmail('');
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
