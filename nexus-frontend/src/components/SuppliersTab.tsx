import React, { useState, useEffect, useRef } from 'react';
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

interface MineResult {
  company_name?: string;
  website?: string;
  ai_score?: number;
  source?: string;
  [key: string]: any;
}

const SuppliersTab: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  
  // Mining state
  const [miningProduct, setMiningProduct] = useState('');
  const [miningSource, setMiningSource] = useState<string | null>(null);
  const [miningResults, setMiningResults] = useState<MineResult[]>([]);
  const [isMining, setIsMining] = useState(false);
  
  // Product search state
  const [productSearch, setProductSearch] = useState('');
  const [productResults, setProductResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // CSV import
  const [isDragging, setIsDragging] = useState(false);
  const csvInputRef = useRef<HTMLInputElement>(null);

  // Active sub-tab
  const [activeSection, setActiveSection] = useState<'database' | 'mine' | 'search'>('database');

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
      showNotif('Failed to load suppliers', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotif = (message: string, type: 'success' | 'error' | 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleAddSupplier = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createGpssSupplier(formData);
      showNotif('Supplier added successfully!', 'success');
      setShowAddModal(false);
      resetForm();
      fetchSuppliers();
    } catch (error) {
      console.error('Error adding supplier:', error);
      showNotif('Failed to add supplier', 'error');
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
      showNotif('Supplier updated successfully!', 'success');
      setSelectedSupplier(null);
      resetForm();
      fetchSuppliers();
    } catch (error) {
      console.error('Error updating supplier:', error);
      showNotif('Failed to update supplier', 'error');
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
      'Business Status': supplier.business_status || 'Prospective',
      'Typical Margin (%)': supplier.typical_margin,
      'Discovery Method': supplier.discovery_method || 'Manual Entry',
      'Discovered By': supplier.discovered_by || 'Dee Davis'
    });
  };

  // ========== MINING ==========
  const handleMine = async (source: string) => {
    if (!miningProduct.trim()) {
      showNotif('Enter a product or keyword to mine', 'error');
      return;
    }
    setIsMining(true);
    setMiningSource(source);
    setMiningResults([]);
    try {
      let result;
      switch (source) {
        case 'thomasnet':
          result = await api.mineSuppliersThomasnet(miningProduct);
          break;
        case 'google':
          result = await api.mineSuppliersGoogle(miningProduct);
          break;
        case 'gsa':
          result = await api.mineSuppliersGsa(miningProduct);
          break;
        case 'all':
          result = await api.mineSuppliersAll(miningProduct);
          break;
        default:
          return;
      }
      const found = result.suppliers || result.results || [];
      setMiningResults(found);
      showNotif(`Found ${found.length} suppliers from ${source === 'all' ? 'all sources' : source}`, 'success');
      // Refresh the supplier list since mining may auto-import
      fetchSuppliers();
    } catch (error: any) {
      console.error('Mining error:', error);
      showNotif(error.message || 'Mining failed', 'error');
    } finally {
      setIsMining(false);
      setMiningSource(null);
    }
  };

  // ========== PRODUCT SEARCH ==========
  const handleProductSearch = async () => {
    if (!productSearch.trim()) {
      showNotif('Enter a product to search for', 'error');
      return;
    }
    setIsSearching(true);
    setProductResults([]);
    try {
      const result = await api.findSuppliersForProduct(productSearch);
      setProductResults(result.suppliers || []);
      showNotif(`Found ${(result.suppliers || []).length} suppliers for "${productSearch}"`, 'success');
    } catch (error: any) {
      console.error('Product search error:', error);
      showNotif(error.message || 'Search failed', 'error');
    } finally {
      setIsSearching(false);
    }
  };

  // ========== RATING ==========
  const handleRate = async (supplierId: string, outcome: string) => {
    try {
      const result = await api.rateSupplier(supplierId, outcome);
      if (result.success) {
        showNotif(
          `Rating updated: ${result.previous_rating} → ${result.new_rating} stars (${outcome.replace(/_/g, ' ')})`,
          'success'
        );
        fetchSuppliers();
      } else {
        showNotif(result.error || 'Rating failed', 'error');
      }
    } catch (error: any) {
      showNotif(error.message || 'Rating failed', 'error');
    }
  };

  // ========== CSV IMPORT ==========
  const handleCsvImport = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      showNotif('Please upload a CSV file', 'error');
      return;
    }
    setLoading(true);
    try {
      const result = await api.importSuppliersCsv(file);
      showNotif(
        `Imported ${result.imported || 0} suppliers (${result.skipped || 0} skipped, ${result.errors || 0} errors)`,
        'success'
      );
      fetchSuppliers();
    } catch (error: any) {
      showNotif(error.message || 'CSV import failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleCsvImport(file);
  };

  // ========== FILTERING ==========
  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = supplier.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (supplier.product_keywords || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (supplier.contact_email || '').toLowerCase().includes(searchTerm.toLowerCase());
    const normalizedStatus = supplier.business_status || 'Unknown';
    const matchesStatus = filterStatus === 'all' || normalizedStatus === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Prospective': return 'bg-yellow-100 text-yellow-800';
      case 'Inactive': return 'bg-gray-100 text-gray-800';
      case 'Blacklisted': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={i <= Math.round(rating) ? 'text-yellow-500' : 'text-gray-300'}>
          ★
        </span>
      );
    }
    return <span className="text-lg">{stars}</span>;
  };

  // Stats
  const totalSuppliers = suppliers.length;
  const activeCount = suppliers.filter(s => s.business_status === 'Active').length;
  const withTerms = suppliers.filter(s => s.net_30_available || s.net_45_available).length;
  const highRated = suppliers.filter(s => s.overall_rating >= 4).length;
  const withContacts = suppliers.filter(s => s.contact_email || s.phone).length;
  const unknownStatus = suppliers.filter(s => !s.business_status).length;

  return (
    <div className="space-y-6">
      {/* Notification */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white font-medium ${
          notification.type === 'success' ? 'bg-green-600' :
          notification.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        }`}>
          {notification.message}
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Supplier Intelligence</h2>
          <p className="text-gray-600 mt-1">
            Database + Mining + Performance Tracking — {totalSuppliers} suppliers
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { resetForm(); setShowAddModal(true); }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
          >
            + Add Supplier
          </button>
          <button
            onClick={fetchSuppliers}
            disabled={loading}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-gray-500">
          <div className="text-2xl font-bold text-gray-900">{totalSuppliers}</div>
          <div className="text-xs text-gray-500 font-medium">TOTAL</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <div className="text-2xl font-bold text-green-600">{activeCount}</div>
          <div className="text-xs text-gray-500 font-medium">ACTIVE</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
          <div className="text-2xl font-bold text-blue-600">{withTerms}</div>
          <div className="text-xs text-gray-500 font-medium">WITH TERMS</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-yellow-500">
          <div className="text-2xl font-bold text-yellow-600">{highRated}</div>
          <div className="text-xs text-gray-500 font-medium">4+ STARS</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
          <div className="text-2xl font-bold text-purple-600">{withContacts}</div>
          <div className="text-xs text-gray-500 font-medium">WITH CONTACTS</div>
        </div>
        {unknownStatus > 0 && (
          <div className="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
            <div className="text-2xl font-bold text-orange-600">{unknownStatus}</div>
            <div className="text-xs text-gray-500 font-medium">NEEDS STATUS</div>
          </div>
        )}
      </div>

      {/* Sub-navigation */}
      <div className="bg-white rounded-lg shadow">
        <div className="flex border-b">
          <button
            onClick={() => setActiveSection('database')}
            className={`px-6 py-3 font-medium text-sm border-b-2 ${
              activeSection === 'database'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Supplier Database ({totalSuppliers})
          </button>
          <button
            onClick={() => setActiveSection('mine')}
            className={`px-6 py-3 font-medium text-sm border-b-2 ${
              activeSection === 'mine'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Mine Suppliers
          </button>
          <button
            onClick={() => setActiveSection('search')}
            className={`px-6 py-3 font-medium text-sm border-b-2 ${
              activeSection === 'search'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Find by Product
          </button>
        </div>

        {/* ================== DATABASE SECTION ================== */}
        {activeSection === 'database' && (
          <div className="p-4 space-y-4">
            {/* Filters + CSV Import */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex gap-3 flex-1">
                <input
                  type="text"
                  placeholder="Search suppliers, keywords, emails..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="flex-1 px-4 py-2 border rounded-lg text-sm"
                />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border rounded-lg text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="Active">Active</option>
                  <option value="Prospective">Prospective</option>
                  <option value="Unknown">Needs Status</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
              
              {/* CSV Import Zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => csvInputRef.current?.click()}
                className={`px-4 py-2 border-2 border-dashed rounded-lg text-sm cursor-pointer text-center min-w-[160px] ${
                  isDragging
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 text-gray-500 hover:border-gray-400 hover:bg-gray-50'
                }`}
              >
                Drop CSV or Click to Import
                <input
                  ref={csvInputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleCsvImport(file);
                    e.target.value = '';
                  }}
                />
              </div>
            </div>

            {/* Supplier Table */}
            {loading ? (
              <div className="p-8 text-center text-gray-600">Loading suppliers...</div>
            ) : filteredSuppliers.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <div className="text-4xl mb-2">🏭</div>
                <p className="font-medium">No suppliers found</p>
                <p className="text-sm mt-1">
                  {searchTerm || filterStatus !== 'all'
                    ? 'Try changing your search or filter'
                    : 'Add suppliers manually or use the Mine tab to discover them'}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Products</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Terms</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredSuppliers.map((supplier) => (
                      <React.Fragment key={supplier.id}>
                        <tr
                          className="hover:bg-gray-50 cursor-pointer transition-colors"
                          onClick={() => setExpandedId(expandedId === supplier.id ? null : supplier.id)}
                        >
                          <td className="px-4 py-3">
                            <div className="font-medium text-gray-900">{supplier.company_name}</div>
                            {supplier.website && (
                              <a
                                href={supplier.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:underline"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {supplier.website.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]}
                              </a>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {supplier.contact_email && (
                              <div className="truncate max-w-[180px]">{supplier.contact_email}</div>
                            )}
                            {supplier.phone && <div>{supplier.phone}</div>}
                            {!supplier.contact_email && !supplier.phone && (
                              <span className="text-gray-400 text-xs">No contact info</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            <div className="max-w-[200px] truncate" title={supplier.product_keywords || ''}>
                              {supplier.product_keywords || <span className="text-gray-400">—</span>}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {supplier.net_30_available && <div className="text-green-700 text-xs font-medium">Net 30</div>}
                            {supplier.net_45_available && <div className="text-green-700 text-xs font-medium">Net 45</div>}
                            {!supplier.net_30_available && !supplier.net_45_available && (
                              <span className="text-gray-400 text-xs">None</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            {renderStars(supplier.overall_rating)}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(supplier.business_status || 'Unknown')}`}>
                              {supplier.business_status || 'Unknown'}
                            </span>
                          </td>
                        </tr>

                        {/* Expanded Detail Row */}
                        {expandedId === supplier.id && (
                          <tr className="bg-gray-50">
                            <td colSpan={6} className="px-4 py-4">
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {/* Col 1: Details */}
                                <div className="space-y-2">
                                  <h4 className="font-semibold text-gray-900 text-sm">Details</h4>
                                  <div className="text-xs space-y-1 text-gray-600">
                                    <div><span className="font-medium">Margin:</span> {supplier.typical_margin > 0 ? `${supplier.typical_margin}%` : 'Not set'}</div>
                                    <div><span className="font-medium">Discovered:</span> {supplier.discovery_date || 'Unknown'}</div>
                                    <div><span className="font-medium">Method:</span> {supplier.discovery_method || 'Unknown'}</div>
                                    <div><span className="font-medium">Added by:</span> {supplier.discovered_by || 'Unknown'}</div>
                                  </div>
                                  <div className="text-xs text-gray-500 mt-2">
                                    <span className="font-medium">Full Keywords:</span>
                                    <div className="mt-1 text-gray-700">{supplier.product_keywords || 'None'}</div>
                                  </div>
                                </div>

                                {/* Col 2: Performance Rating */}
                                <div className="space-y-2">
                                  <h4 className="font-semibold text-gray-900 text-sm">Rate Performance</h4>
                                  <p className="text-xs text-gray-500">Click to record a supplier outcome — the system learns and adjusts ratings automatically.</p>
                                  <div className="grid grid-cols-2 gap-1">
                                    <button onClick={() => handleRate(supplier.id, 'quote_received_fast')}
                                      className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200">
                                      Fast Quote (+1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'competitive_price')}
                                      className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200">
                                      Good Price (+1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'won_with_supplier')}
                                      className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200">
                                      Won Contract (+1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'reliable_delivery')}
                                      className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200">
                                      On-Time Delivery (+1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'quote_late')}
                                      className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200">
                                      Late Quote (-1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'no_response')}
                                      className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200">
                                      No Response (-1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'overpriced')}
                                      className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200">
                                      Overpriced (-1)
                                    </button>
                                    <button onClick={() => handleRate(supplier.id, 'late_delivery')}
                                      className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200">
                                      Late Delivery (-1)
                                    </button>
                                  </div>
                                </div>

                                {/* Col 3: Actions */}
                                <div className="space-y-2">
                                  <h4 className="font-semibold text-gray-900 text-sm">Actions</h4>
                                  <div className="flex flex-col gap-2">
                                    <button
                                      onClick={(e) => { e.stopPropagation(); openEditModal(supplier); }}
                                      className="px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
                                    >
                                      Edit Supplier Info
                                    </button>
                                    {supplier.contact_email && (
                                      <a
                                        href={`mailto:${supplier.contact_email}`}
                                        className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        Email: {supplier.contact_email}
                                      </a>
                                    )}
                                    {supplier.phone && (
                                      <a
                                        href={`tel:${supplier.phone}`}
                                        className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        Call: {supplier.phone}
                                      </a>
                                    )}
                                    {supplier.website && (
                                      <a
                                        href={supplier.website}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        Visit Website
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="text-xs text-gray-400 text-right">
              Showing {filteredSuppliers.length} of {totalSuppliers} suppliers
            </div>
          </div>
        )}

        {/* ================== MINE SECTION ================== */}
        {activeSection === 'mine' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-bold text-gray-900">Supplier Mining Engine</h3>
              <p className="text-sm text-gray-600 mt-1">
                Search ThomasNet, Google, and GSA Advantage to discover new suppliers. 
                Found suppliers are automatically added to your database.
              </p>
            </div>

            {/* Mining Input */}
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Enter product or keyword (e.g., industrial wipers, office chairs, safety gloves)"
                value={miningProduct}
                onChange={(e) => setMiningProduct(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleMine('all')}
                className="flex-1 px-4 py-3 border rounded-lg text-sm"
              />
            </div>

            {/* Mining Source Buttons */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                onClick={() => handleMine('thomasnet')}
                disabled={isMining}
                className="p-4 bg-white border-2 rounded-lg hover:border-blue-500 hover:bg-blue-50 text-left transition-colors disabled:opacity-50"
              >
                <div className="font-bold text-sm text-gray-900">ThomasNet</div>
                <div className="text-xs text-gray-500 mt-1">Industrial supplier directory</div>
                {isMining && miningSource === 'thomasnet' && (
                  <div className="text-xs text-blue-600 mt-2 animate-pulse">Mining...</div>
                )}
              </button>
              <button
                onClick={() => handleMine('google')}
                disabled={isMining}
                className="p-4 bg-white border-2 rounded-lg hover:border-green-500 hover:bg-green-50 text-left transition-colors disabled:opacity-50"
              >
                <div className="font-bold text-sm text-gray-900">Google Search</div>
                <div className="text-xs text-gray-500 mt-1">Web-wide supplier search</div>
                {isMining && miningSource === 'google' && (
                  <div className="text-xs text-green-600 mt-2 animate-pulse">Mining...</div>
                )}
              </button>
              <button
                onClick={() => handleMine('gsa')}
                disabled={isMining}
                className="p-4 bg-white border-2 rounded-lg hover:border-purple-500 hover:bg-purple-50 text-left transition-colors disabled:opacity-50"
              >
                <div className="font-bold text-sm text-gray-900">GSA Advantage</div>
                <div className="text-xs text-gray-500 mt-1">Government contract holders</div>
                {isMining && miningSource === 'gsa' && (
                  <div className="text-xs text-purple-600 mt-2 animate-pulse">Mining...</div>
                )}
              </button>
              <button
                onClick={() => handleMine('all')}
                disabled={isMining}
                className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white border-2 border-transparent rounded-lg hover:from-blue-700 hover:to-purple-700 text-left transition-colors disabled:opacity-50"
              >
                <div className="font-bold text-sm">Mine ALL Sources</div>
                <div className="text-xs opacity-80 mt-1">ThomasNet + Google + GSA</div>
                {isMining && miningSource === 'all' && (
                  <div className="text-xs mt-2 animate-pulse">Mining all sources...</div>
                )}
              </button>
            </div>

            {/* Mining Results */}
            {miningResults.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">
                  Mining Results ({miningResults.length} suppliers found)
                </h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-100 border-b">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {miningResults.map((r, i) => (
                        <tr key={i} className="hover:bg-white">
                          <td className="px-4 py-2 text-sm font-medium text-gray-900">
                            {r.company_name || r['COMPANY NAME'] || 'Unknown'}
                          </td>
                          <td className="px-4 py-2 text-sm">
                            {(r.website || r['WEBSITE']) ? (
                              <a
                                href={r.website || r['WEBSITE']}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline text-xs"
                              >
                                {(r.website || r['WEBSITE'] || '').replace(/^https?:\/\/(www\.)?/, '').split('/')[0]}
                              </a>
                            ) : <span className="text-gray-400 text-xs">—</span>}
                          </td>
                          <td className="px-4 py-2 text-xs text-gray-500">
                            {r.source || r['DISCOVERY METHOD'] || '—'}
                          </td>
                          <td className="px-4 py-2 text-sm font-medium">
                            {r.ai_score ? `${r.ai_score}/100` : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  These suppliers have been automatically added to your database.
                </p>
              </div>
            )}

            {/* Mining Tips */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 text-sm">Tips for Better Mining Results</h4>
              <ul className="mt-2 space-y-1 text-xs text-blue-800">
                <li>Use specific product names: "stainless steel bolts" not just "bolts"</li>
                <li>ThomasNet is best for industrial/manufacturing suppliers</li>
                <li>Google finds a wider range including distributors and resellers</li>
                <li>GSA Advantage finds suppliers already approved for government contracts</li>
                <li>"Mine ALL" runs all three and deduplicates automatically</li>
              </ul>
            </div>
          </div>
        )}

        {/* ================== PRODUCT SEARCH SECTION ================== */}
        {activeSection === 'search' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-bold text-gray-900">Find Suppliers by Product</h3>
              <p className="text-sm text-gray-600 mt-1">
                Search your database first, then automatically mine the web if more suppliers are needed.
                This is the smart search — it checks your existing suppliers before going external.
              </p>
            </div>

            <div className="flex gap-3">
              <input
                type="text"
                placeholder="What product do you need a supplier for? (e.g., copy paper, road salt, safety gloves)"
                value={productSearch}
                onChange={(e) => setProductSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleProductSearch()}
                className="flex-1 px-4 py-3 border rounded-lg text-sm"
              />
              <button
                onClick={handleProductSearch}
                disabled={isSearching}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm disabled:opacity-50"
              >
                {isSearching ? 'Searching...' : 'Find Suppliers'}
              </button>
            </div>

            {/* Product Search Results */}
            {productResults.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">
                  Matching Suppliers ({productResults.length})
                </h4>
                <div className="space-y-3">
                  {productResults.map((s, i) => (
                    <div key={i} className="bg-white border rounded-lg p-4 flex justify-between items-start">
                      <div>
                        <div className="font-medium text-gray-900">{s.company_name || s['COMPANY NAME'] || 'Unknown'}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          {s.product_keywords || s['PRODUCT KEYWORDS'] || ''}
                        </div>
                        <div className="flex gap-4 mt-2 text-xs text-gray-500">
                          {s.contact_email && <span>{s.contact_email}</span>}
                          {s.phone && <span>{s.phone}</span>}
                          {s.website && (
                            <a href={s.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                              Website
                            </a>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div>{renderStars(s.overall_rating || 0)}</div>
                        {s.ai_score && (
                          <div className="text-xs text-gray-500 mt-1">Score: {s.ai_score}/100</div>
                        )}
                        <div className="text-xs mt-1">
                          <span className={`px-2 py-0.5 rounded-full ${getStatusColor(s.business_status || 'Unknown')}`}>
                            {s.business_status || 'Unknown'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {productResults.length === 0 && productSearch && !isSearching && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-3xl mb-2">🔍</div>
                <p className="font-medium">No results yet</p>
                <p className="text-sm">Click "Find Suppliers" to search your database and the web</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ================== ADD/EDIT MODAL ================== */}
      {(showAddModal || selectedSupplier) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">
                {selectedSupplier ? `Edit: ${selectedSupplier.company_name}` : 'Add New Supplier'}
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
                    <input
                      type="url"
                      value={formData['Website']}
                      onChange={(e) => setFormData({...formData, 'Website': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="https://"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contact Email</label>
                    <input
                      type="email"
                      value={formData['Primary Contact Email']}
                      onChange={(e) => setFormData({...formData, 'Primary Contact Email': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contact Phone</label>
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">Business Status</label>
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">Typical Margin (%)</label>
                    <input
                      type="number"
                      value={formData['Typical Margin (%)']}
                      onChange={(e) => setFormData({...formData, 'Typical Margin (%)': parseFloat(e.target.value) || 0})}
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
