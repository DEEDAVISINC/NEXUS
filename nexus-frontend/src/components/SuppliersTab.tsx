import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface Supplier {
  id: string;
  company_name: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  product_keywords?: string;
  net_30_available: boolean;
  net_45_available: boolean;
  business_status: string;
  typical_margin: number;
  overall_rating: number;
  discovery_method?: string;
  discovery_date?: string;
  discovered_by?: string;
  last_order_date?: string;
}

const SuppliersTab: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  const [formData, setFormData] = useState({
    'Company Name': '',
    'Website': '',
    'Primary Contact Email': '',
    'Primary Contact Phone': '',
    'Product Keywords': '',
    'Net 30 Available': false,
    'Net 45 Available': false,
    'Business Status': 'Prospective',
    'Typical Margin (%)': 20,
    'Discovery Method': 'Manual Entry',
    'Discovered By': 'Dee Davis'
  });

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const response = await api.getGpssSuppliers();
      setSuppliers(response.suppliers || []);
    } catch (error) {
      console.error('Error fetching suppliers:', error);
      showNotification('Failed to load suppliers', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createGpssSupplier(formData);
      showNotification('Supplier added successfully!', 'success');
      setShowAddModal(false);
      resetForm();
      fetchSuppliers();
    } catch (error) {
      console.error('Error adding supplier:', error);
      showNotification('Failed to add supplier', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSupplier) return;
    
    setLoading(true);
    try {
      await api.updateGpssSupplier(selectedSupplier.id, formData);
      showNotification('Supplier updated successfully!', 'success');
      setSelectedSupplier(null);
      resetForm();
      fetchSuppliers();
    } catch (error) {
      console.error('Error updating supplier:', error);
      showNotification('Failed to update supplier', 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      'Company Name': '',
      'Website': '',
      'Primary Contact Email': '',
      'Primary Contact Phone': '',
      'Product Keywords': '',
      'Net 30 Available': false,
      'Net 45 Available': false,
      'Business Status': 'Prospective',
      'Typical Margin (%)': 20,
      'Discovery Method': 'Manual Entry',
      'Discovered By': 'Dee Davis'
    });
  };

  const openEditModal = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setFormData({
      'Company Name': supplier.company_name,
      'Website': supplier.website || '',
      'Primary Contact Email': supplier.contact_email || '',
      'Primary Contact Phone': supplier.phone || '',
      'Product Keywords': supplier.product_keywords || '',
      'Net 30 Available': supplier.net_30_available,
      'Net 45 Available': supplier.net_45_available,
      'Business Status': supplier.business_status,
      'Typical Margin (%)': supplier.typical_margin,
      'Discovery Method': supplier.discovery_method || 'Manual Entry',
      'Discovered By': supplier.discovered_by || 'Dee Davis'
    });
  };

  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = supplier.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (supplier.product_keywords || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || supplier.business_status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Prospective': return 'bg-yellow-100 text-yellow-800';
      case 'Inactive': return 'bg-gray-100 text-gray-800';
      case 'Blacklisted': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderStars = (rating: number) => {
    return '⭐'.repeat(Math.round(rating));
  };

  return (
    <div className="space-y-6">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white font-medium`}>
          {notification.message}
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🏭 Supplier Database</h2>
          <p className="text-gray-600">Manage your supplier relationships and payment terms</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowAddModal(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          ➕ Add Supplier
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-gray-900">{suppliers.length}</div>
          <div className="text-sm text-gray-600">Total Suppliers</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {suppliers.filter(s => s.business_status === 'Active').length}
          </div>
          <div className="text-sm text-gray-600">Active</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600">
            {suppliers.filter(s => s.net_30_available).length}
          </div>
          <div className="text-sm text-gray-600">Net 30 Available</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-purple-600">
            {suppliers.filter(s => s.overall_rating >= 4).length}
          </div>
          <div className="text-sm text-gray-600">4+ Star Rated</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow flex gap-4">
        <input
          type="text"
          placeholder="🔍 Search suppliers or keywords..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">All Status</option>
          <option value="Active">Active</option>
          <option value="Prospective">Prospective</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>

      {/* Suppliers Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-600">Loading suppliers...</div>
        ) : filteredSuppliers.length === 0 ? (
          <div className="p-8 text-center text-gray-600">
            No suppliers found. Click "Add Supplier" to get started!
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Keywords</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Terms</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Margin</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSuppliers.map((supplier) => (
                <tr key={supplier.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{supplier.company_name}</div>
                    {supplier.website && (
                      <a href={supplier.website} target="_blank" rel="noopener noreferrer" 
                         className="text-sm text-blue-600 hover:underline">
                        Visit Website →
                      </a>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {supplier.contact_email && <div>{supplier.contact_email}</div>}
                    {supplier.phone && <div>{supplier.phone}</div>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    <div className="max-w-xs truncate">
                      {supplier.product_keywords || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {supplier.net_30_available && <div className="text-green-600">✓ Net 30</div>}
                    {supplier.net_45_available && <div className="text-green-600">✓ Net 45</div>}
                    {!supplier.net_30_available && !supplier.net_45_available && (
                      <div className="text-gray-400">No terms</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {supplier.typical_margin}%
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {supplier.overall_rating > 0 ? renderStars(supplier.overall_rating) : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(supplier.business_status)}`}>
                      {supplier.business_status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => openEditModal(supplier)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || selectedSupplier) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">
                {selectedSupplier ? 'Edit Supplier' : 'Add New Supplier'}
              </h3>
              
              <form onSubmit={selectedSupplier ? handleUpdateSupplier : handleAddSupplier} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData['Company Name']}
                    onChange={(e) => setFormData({...formData, 'Company Name': e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Website
                    </label>
                    <input
                      type="url"
                      value={formData['Website']}
                      onChange={(e) => setFormData({...formData, 'Website': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="https://"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Contact Email
                    </label>
                    <input
                      type="email"
                      value={formData['Primary Contact Email']}
                      onChange={(e) => setFormData({...formData, 'Primary Contact Email': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    value={formData['Primary Contact Phone']}
                    onChange={(e) => setFormData({...formData, 'Primary Contact Phone': e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Product Keywords (comma-separated)
                  </label>
                  <textarea
                    value={formData['Product Keywords']}
                    onChange={(e) => setFormData({...formData, 'Product Keywords': e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg"
                    rows={2}
                    placeholder="paper, office supplies, toner, etc."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Business Status
                    </label>
                    <select
                      value={formData['Business Status']}
                      onChange={(e) => setFormData({...formData, 'Business Status': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="Active">Active</option>
                      <option value="Prospective">Prospective</option>
                      <option value="Inactive">Inactive</option>
                      <option value="Blacklisted">Blacklisted</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Typical Margin (%)
                    </label>
                    <input
                      type="number"
                      value={formData['Typical Margin (%)']}
                      onChange={(e) => setFormData({...formData, 'Typical Margin (%)': parseFloat(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-lg"
                      min="0"
                      max="100"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData['Net 30 Available']}
                      onChange={(e) => setFormData({...formData, 'Net 30 Available': e.target.checked})}
                      className="rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Net 30 Terms Available</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData['Net 45 Available']}
                      onChange={(e) => setFormData({...formData, 'Net 45 Available': e.target.checked})}
                      className="rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Net 45 Terms Available</span>
                  </label>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
                  >
                    {loading ? 'Saving...' : (selectedSupplier ? 'Update Supplier' : 'Add Supplier')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setSelectedSupplier(null);
                      resetForm();
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuppliersTab;
