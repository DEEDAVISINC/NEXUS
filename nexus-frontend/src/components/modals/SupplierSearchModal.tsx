import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';

interface SupplierSearchModalProps {
  opportunity: any;
  onClose: () => void;
  onSuccess: () => void;
}

export const SupplierSearchModal: React.FC<SupplierSearchModalProps> = ({
  opportunity,
  onClose,
  onSuccess
}) => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [filteredSuppliers, setFilteredSuppliers] = useState<any[]>([]);
  const [selectedSuppliers, setSelectedSuppliers] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterState, setFilterState] = useState('all');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load suppliers
  useEffect(() => {
    loadSuppliers();
  }, []);

  // Filter suppliers when search/filters change
  useEffect(() => {
    filterSuppliers();
  }, [searchTerm, filterCategory, filterState, suppliers]);

  const loadSuppliers = async () => {
    setLoading(true);
    try {
      const response = await api.getGpssSuppliers();
      setSuppliers(response || []);
    } catch (error) {
      console.error('Error loading suppliers:', error);
      
      // Mock suppliers for testing
      const mockSuppliers = [
        {
          id: 'mock-sup-1',
          fields: {
            'Name': 'Grainger Industrial Supply',
            'Category': 'Industrial Supplies',
            'State': 'Illinois',
            'Contact Name': 'John Smith',
            'Email': 'quotes@grainger.com',
            'Phone': '800-472-4643',
            'Products': 'Industrial wipers, safety supplies, cleaning products, tools',
            'Capabilities': 'National distribution, next-day delivery, bulk pricing',
            'Website': 'www.grainger.com'
          }
        },
        {
          id: 'mock-sup-2',
          fields: {
            'Name': 'Fastenal Company',
            'Category': 'Industrial Supplies',
            'State': 'Minnesota',
            'Contact Name': 'Sarah Johnson',
            'Email': 'rfq@fastenal.com',
            'Phone': '507-454-5374',
            'Products': 'Fasteners, tools, safety supplies, industrial products',
            'Capabilities': '3,000+ locations, same-day delivery, vending solutions',
            'Website': 'www.fastenal.com'
          }
        },
        {
          id: 'mock-sup-3',
          fields: {
            'Name': 'MSC Industrial Supply',
            'Category': 'Industrial Supplies',
            'State': 'New York',
            'Contact Name': 'Mike Davis',
            'Email': 'quotes@mscdirect.com',
            'Phone': '800-645-7270',
            'Products': 'Metalworking tools, safety supplies, janitorial products',
            'Capabilities': '2M+ products, expert technical support, VMI programs',
            'Website': 'www.mscdirect.com'
          }
        },
        {
          id: 'mock-sup-4',
          fields: {
            'Name': 'Medline Industries',
            'Category': 'Medical Supplies',
            'State': 'Illinois',
            'Contact Name': 'Dr. Lisa Chen',
            'Email': 'governmentsales@medline.com',
            'Phone': '800-633-5463',
            'Products': 'Body bags, medical examination supplies, PPE',
            'Capabilities': 'Medical-grade products, GSA contract holder, certified quality',
            'Website': 'www.medline.com'
          }
        },
        {
          id: 'mock-sup-5',
          fields: {
            'Name': 'McKesson Medical-Surgical',
            'Category': 'Medical Supplies',
            'State': 'Texas',
            'Contact Name': 'Robert Martinez',
            'Email': 'quotes@mckesson.com',
            'Phone': '888-625-3776',
            'Products': 'Medical supplies, lab equipment, diagnostic products',
            'Capabilities': 'Full-service distribution, regulatory compliance, training',
            'Website': 'www.mckesson.com'
          }
        },
        {
          id: 'mock-sup-6',
          fields: {
            'Name': 'Aggregate Industries',
            'Category': 'Aggregate Materials',
            'State': 'Michigan',
            'Contact Name': 'Tom Wilson',
            'Email': 'quotes@aggregate-us.com',
            'Phone': '248-555-0100',
            'Products': 'Limestone, sand, gravel, crushed concrete',
            'Capabilities': 'MDOT certified, 2-day delivery, bulk pricing',
            'Website': 'www.aggregate-us.com'
          }
        },
        {
          id: 'mock-sup-7',
          fields: {
            'Name': 'Martin Marietta Materials',
            'Category': 'Aggregate Materials',
            'State': 'Michigan',
            'Contact Name': 'Jennifer Brown',
            'Email': 'bids@martinmarietta.com',
            'Phone': '919-781-4550',
            'Products': 'Crushed stone, sand, gravel, asphalt, concrete',
            'Capabilities': 'Large volume capacity, quality testing, municipal contracts',
            'Website': 'www.martinmarietta.com'
          }
        },
        {
          id: 'mock-sup-8',
          fields: {
            'Name': 'Sunbelt Mill Supply',
            'Category': 'Industrial Supplies',
            'State': 'Texas',
            'Contact Name': 'David Lee',
            'Email': 'sales@sunbeltmill.com',
            'Phone': '210-555-0200',
            'Products': 'Industrial wipers, safety supplies, MRO products',
            'Capabilities': 'Regional supplier, competitive pricing, quick turnaround',
            'Website': 'www.sunbeltmill.com'
          }
        }
      ];
      setSuppliers(mockSuppliers);
    } finally {
      setLoading(false);
    }
  };

  const filterSuppliers = () => {
    let filtered = suppliers;

    // Search term filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(s => 
        s.fields['Name']?.toLowerCase().includes(search) ||
        s.fields['Products']?.toLowerCase().includes(search) ||
        s.fields['Category']?.toLowerCase().includes(search) ||
        s.fields['State']?.toLowerCase().includes(search)
      );
    }

    // Category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(s => s.fields['Category'] === filterCategory);
    }

    // State filter
    if (filterState !== 'all') {
      filtered = filtered.filter(s => s.fields['State'] === filterState);
    }

    setFilteredSuppliers(filtered);
  };

  const toggleSupplier = (supplierId: string) => {
    const newSelected = new Set(selectedSuppliers);
    if (newSelected.has(supplierId)) {
      newSelected.delete(supplierId);
    } else {
      newSelected.add(supplierId);
    }
    setSelectedSuppliers(newSelected);
  };

  const handleSubmit = async () => {
    if (selectedSuppliers.size === 0) {
      setError('Please select at least one supplier');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await api.identifySuppliers(
        opportunity.id,
        Array.from(selectedSuppliers)
      );

      if (response.success) {
        onSuccess();
        onClose();
      } else {
        setError(response.error || 'Failed to add suppliers');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  // Get unique categories and states for filters
  const categories = Array.from(new Set(suppliers.map(s => s.fields['Category']).filter(Boolean)));
  const states = Array.from(new Set(suppliers.map(s => s.fields['State']).filter(Boolean)));

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-xl border border-gray-700 max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-4 border-b border-gray-700 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-black text-white">🔎 Find Suppliers</h2>
              <p className="text-sm text-purple-100 mt-1">
                Search and select suppliers for: <span className="font-bold">{opportunity.fields.Name}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition text-2xl font-bold"
              disabled={submitting}
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            {/* Search Bar */}
            <div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="🔍 Search suppliers by name, products, location..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition"
              />
            </div>

            {/* Filters */}
            <div className="flex gap-3">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>

              <select
                value={filterState}
                onChange={(e) => setFilterState(e.target.value)}
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition"
              >
                <option value="all">All States</option>
                {states.sort().map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>

            {/* Selected Count */}
            {selectedSuppliers.size > 0 && (
              <div className="flex items-center justify-between p-3 bg-purple-900/20 border border-purple-500/30 rounded-lg">
                <span className="text-sm text-purple-300">
                  <span className="font-bold text-purple-400">{selectedSuppliers.size}</span> supplier{selectedSuppliers.size !== 1 ? 's' : ''} selected
                </span>
                <button
                  onClick={() => setSelectedSuppliers(new Set())}
                  className="text-xs text-purple-400 hover:text-purple-300 font-bold"
                >
                  Clear All
                </button>
              </div>
            )}
          </div>

          {/* Suppliers List */}
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
              <p className="text-gray-400 mt-3">Loading suppliers...</p>
            </div>
          ) : filteredSuppliers.length === 0 ? (
            <div className="text-center py-12 bg-gray-800/50 border border-gray-700 rounded-lg">
              <div className="text-4xl mb-3">🔍</div>
              <p className="text-gray-400">No suppliers found matching your criteria</p>
              <p className="text-sm text-gray-500 mt-2">Try adjusting your search or filters</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredSuppliers.map((supplier) => {
                const isSelected = selectedSuppliers.has(supplier.id);
                return (
                  <div
                    key={supplier.id}
                    onClick={() => toggleSupplier(supplier.id)}
                    className={`p-4 rounded-lg border-2 transition cursor-pointer ${
                      isSelected
                        ? 'bg-purple-900/30 border-purple-500'
                        : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Checkbox */}
                      <div className="mt-1">
                        <div className={`w-6 h-6 rounded border-2 flex items-center justify-center transition ${
                          isSelected
                            ? 'bg-purple-600 border-purple-600'
                            : 'bg-gray-700 border-gray-600'
                        }`}>
                          {isSelected && (
                            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                      </div>

                      {/* Supplier Info */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="text-lg font-bold text-white">{supplier.fields['Name']}</h3>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="text-xs px-2 py-1 bg-blue-900/30 text-blue-400 rounded border border-blue-500/30 font-bold">
                                {supplier.fields['Category']}
                              </span>
                              <span className="text-xs text-gray-400">
                                📍 {supplier.fields['State']}
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="space-y-2 text-sm">
                          {supplier.fields['Products'] && (
                            <div className="flex">
                              <span className="text-gray-400 w-24 flex-shrink-0">Products:</span>
                              <span className="text-gray-300">{supplier.fields['Products']}</span>
                            </div>
                          )}
                          
                          {supplier.fields['Capabilities'] && (
                            <div className="flex">
                              <span className="text-gray-400 w-24 flex-shrink-0">Capabilities:</span>
                              <span className="text-gray-300">{supplier.fields['Capabilities']}</span>
                            </div>
                          )}

                          <div className="flex items-center gap-4 pt-2 border-t border-gray-700">
                            {supplier.fields['Contact Name'] && (
                              <span className="text-xs text-gray-400">
                                👤 {supplier.fields['Contact Name']}
                              </span>
                            )}
                            {supplier.fields['Phone'] && (
                              <span className="text-xs text-gray-400">
                                📞 {supplier.fields['Phone']}
                              </span>
                            )}
                            {supplier.fields['Email'] && (
                              <span className="text-xs text-gray-400">
                                ✉️ {supplier.fields['Email']}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="text-sm text-red-400">❌ {error}</div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-6 mt-6 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-bold transition"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={submitting || selectedSuppliers.size === 0}
            >
              {submitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Adding Suppliers...
                </span>
              ) : (
                `Add ${selectedSuppliers.size} Supplier${selectedSuppliers.size !== 1 ? 's' : ''}`
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
