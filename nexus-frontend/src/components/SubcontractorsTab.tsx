import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface Subcontractor {
  id: string;
  company_name: string;
  service_type: string;
  city: string;
  state: string;
  phone: string;
  email: string;
  website: string;
  description: string;
  discovery_method: string;
  discovery_date: string;
  discovered_by: string;
  relationship_status: string;
  reliability_rating: number;
  response_rate: number;
  contracts_won: number;
  last_contacted: string;
  notes: string;
  source_notes: string;
  naics_codes: string[];
  capabilities: string[];
  certifications: string[];
  socioeconomic_certs: string[];
  psc_codes: string;
  hourly_rates: string;
  employee_count: number;
  annual_revenue: number;
  past_performance: string;
  key_contracts: string;
  past_contracts_count: number;
  total_contract_value: number;
  primary_agencies: string[];
  average_contract_size: number;
  contract_types: string[];
  ai_score: number;
  availability: string;
  performance_rating: number;
  compliance_risk: string;
}

const SubcontractorsTab: React.FC = () => {
  const [subs, setSubs] = useState<Subcontractor[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterService, setFilterService] = useState('all');
  const [filterCerts, setFilterCerts] = useState('all');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);

  // Find modal
  const [showFindModal, setShowFindModal] = useState(false);
  const [findService, setFindService] = useState('');
  const [findLocation, setFindLocation] = useState('');
  const [findRadius, setFindRadius] = useState(25);
  const [findResults, setFindResults] = useState<any[]>([]);
  const [isFinding, setIsFinding] = useState(false);

  // Add/Edit modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingSub, setEditingSub] = useState<Subcontractor | null>(null);
  const [formData, setFormData] = useState({
    'Company Name': '',
    'Service Type': '',
    'City': '',
    'State': '',
    'Phone': '',
    'Email': '',
    'Website': '',
    'Description': '',
    'Employee Count': 0,
    'Annual Revenue': 0,
    'Hourly Rates': '',
    'Relationship Status': '',
    'Notes': '',
  });

  useEffect(() => { fetchSubs(); }, []);

  const fetchSubs = async () => {
    setLoading(true);
    try {
      const response = await api.getGpssSubcontractors();
      setSubs(response.subcontractors || []);
    } catch (error) {
      console.error('Error fetching subcontractors:', error);
      showNotif('Failed to load subcontractors', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotif = (message: string, type: 'success' | 'error' | 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Find subcontractors
  const handleFind = async () => {
    if (!findService || !findLocation) {
      showNotif('Enter a service type and location', 'error');
      return;
    }
    setIsFinding(true);
    setFindResults([]);
    try {
      const response = await api.findSubcontractors(findService, findLocation, findRadius);
      setFindResults(response.results || []);
      showNotif(`Found ${(response.results || []).length} subcontractors`, 'success');
    } catch (error: any) {
      showNotif(error.message || 'Search failed', 'error');
    } finally {
      setIsFinding(false);
    }
  };

  const handleAddFromFind = async (result: any) => {
    try {
      await api.createGpssSubcontractor({
        'Company Name': result.company_name,
        'Website': result.website || '',
        'Phone': result.phone || '',
        'Service Type': findService,
        'City': findLocation,
        'Description': `Found via automated search. ${result.total_reviews || 0} reviews.`,
      });
      showNotif(`${result.company_name} added!`, 'success');
      fetchSubs();
      setFindResults(findResults.filter(r => r.company_name !== result.company_name));
    } catch (error: any) {
      showNotif(error.message || 'Failed to add', 'error');
    }
  };

  // Add/Edit
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingSub) {
        await api.updateGpssSubcontractor(editingSub.id, formData);
        showNotif('Subcontractor updated!', 'success');
      } else {
        await api.createGpssSubcontractor(formData);
        showNotif('Subcontractor added!', 'success');
      }
      setShowAddModal(false);
      setEditingSub(null);
      resetForm();
      fetchSubs();
    } catch (error: any) {
      showNotif(error.message || 'Save failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      'Company Name': '', 'Service Type': '', 'City': '', 'State': '', 'Phone': '',
      'Email': '', 'Website': '', 'Description': '', 'Employee Count': 0,
      'Annual Revenue': 0, 'Hourly Rates': '', 'Relationship Status': '', 'Notes': '',
    });
  };

  const openEdit = (sub: Subcontractor) => {
    setEditingSub(sub);
    setFormData({
      'Company Name': sub.company_name,
      'Service Type': sub.service_type,
      'City': sub.city,
      'State': sub.state,
      'Phone': sub.phone,
      'Email': sub.email,
      'Website': sub.website,
      'Description': sub.description,
      'Employee Count': sub.employee_count || 0,
      'Annual Revenue': sub.annual_revenue || 0,
      'Hourly Rates': sub.hourly_rates || '',
      'Relationship Status': sub.relationship_status || '',
      'Notes': sub.notes || '',
    });
    setShowAddModal(true);
  };

  // Filtering
  const serviceTypes = Array.from(new Set(subs.map(s => s.service_type).filter(Boolean)));

  const filtered = subs.filter(sub => {
    const matchSearch = sub.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (sub.service_type || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (sub.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (sub.city || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchService = filterService === 'all' || sub.service_type === filterService;
    const matchCerts = filterCerts === 'all' ||
      (filterCerts === 'small' && (sub.socioeconomic_certs || []).length > 0) ||
      (filterCerts === 'none' && (sub.socioeconomic_certs || []).length === 0);
    return matchSearch && matchService && matchCerts;
  });

  // Stats
  const total = subs.length;
  const withCerts = subs.filter(s => (s.socioeconomic_certs || []).length > 0).length;
  const withContact = subs.filter(s => s.email || s.phone).length;
  const michigan = subs.filter(s => (s.state || '').toUpperCase() === 'MI').length;
  const awaitingQuote = subs.filter(s => (s.relationship_status || '').toLowerCase().includes('awaiting')).length;

  const renderStars = (rating: number) => {
    if (!rating) return <span className="text-gray-300 text-sm">No rating</span>;
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(<span key={i} className={i <= Math.round(rating) ? 'text-yellow-500' : 'text-gray-300'}>★</span>);
    }
    return <span className="text-lg">{stars}</span>;
  };

  const getRelStatusColor = (status: string) => {
    if (!status) return 'bg-gray-100 text-gray-600';
    const s = status.toLowerCase();
    if (s.includes('awaiting')) return 'bg-yellow-100 text-yellow-800';
    if (s.includes('active') || s.includes('working')) return 'bg-green-100 text-green-800';
    if (s.includes('contacted')) return 'bg-blue-100 text-blue-800';
    if (s.includes('not yet')) return 'bg-gray-100 text-gray-600';
    return 'bg-gray-100 text-gray-600';
  };

  const certBadge = (cert: string) => {
    const colors: Record<string, string> = {
      '8(a)': 'bg-purple-100 text-purple-800',
      'HUBZone': 'bg-blue-100 text-blue-800',
      'WOSB': 'bg-pink-100 text-pink-800',
      'EDWOSB': 'bg-pink-200 text-pink-900',
      'VOSB': 'bg-green-100 text-green-800',
      'SDVOSB': 'bg-green-200 text-green-900',
      'MBE': 'bg-orange-100 text-orange-800',
      'SBE': 'bg-teal-100 text-teal-800',
    };
    return colors[cert] || 'bg-gray-100 text-gray-700';
  };

  const isSmallBusiness = (sub: Subcontractor) => {
    return (sub.socioeconomic_certs || []).length > 0 ||
      (sub.employee_count > 0 && sub.employee_count <= 50) ||
      (sub.annual_revenue > 0 && sub.annual_revenue <= 5000000);
  };

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
          <h2 className="text-2xl font-bold text-gray-900">Subcontractor Network</h2>
          <p className="text-gray-600 mt-1">
            {total} subcontractors — Small businesses prioritized
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowFindModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium text-sm">
            Find Subcontractors
          </button>
          <button onClick={() => { resetForm(); setEditingSub(null); setShowAddModal(true); }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm">
            + Add Manually
          </button>
          <button onClick={fetchSubs} disabled={loading}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-gray-500">
          <div className="text-2xl font-bold text-gray-900">{total}</div>
          <div className="text-xs text-gray-500 font-medium">TOTAL SUBS</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-purple-500">
          <div className="text-2xl font-bold text-purple-600">{withCerts}</div>
          <div className="text-xs text-gray-500 font-medium">CERTIFIED SMALL BIZ</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
          <div className="text-2xl font-bold text-blue-600">{michigan}</div>
          <div className="text-xs text-gray-500 font-medium">MICHIGAN</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-yellow-500">
          <div className="text-2xl font-bold text-yellow-600">{awaitingQuote}</div>
          <div className="text-xs text-gray-500 font-medium">AWAITING QUOTE</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
          <div className="text-2xl font-bold text-green-600">{withContact}</div>
          <div className="text-xs text-gray-500 font-medium">WITH CONTACTS</div>
        </div>
      </div>

      {/* Small Business Priority Banner */}
      {withCerts > 0 && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 flex items-center gap-3">
          <div className="text-2xl">⭐</div>
          <div>
            <div className="text-sm font-semibold text-purple-900">Small Business Priority Active</div>
            <div className="text-xs text-purple-700">
              {withCerts} certified small business subcontractors shown first — 8(a), HUBZone, WOSB, SDVOSB, MBE, SBE
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow flex flex-col md:flex-row gap-3">
        <input type="text" placeholder="Search by name, service, city, description..."
          value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg text-sm" />
        <select value={filterService} onChange={e => setFilterService(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm">
          <option value="all">All Services</option>
          {serviceTypes.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={filterCerts} onChange={e => setFilterCerts(e.target.value)}
          className="px-4 py-2 border rounded-lg text-sm">
          <option value="all">All Businesses</option>
          <option value="small">Small Biz Certified</option>
          <option value="none">No Certifications</option>
        </select>
      </div>

      {/* Subcontractors List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-600">Loading subcontractors...</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-2">👷</div>
            <p className="font-medium">No subcontractors found</p>
            <p className="text-sm mt-1">
              {searchTerm || filterService !== 'all' || filterCerts !== 'all'
                ? 'Try changing your filters'
                : 'Use "Find Subcontractors" to search or add manually'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Certs</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(sub => (
                  <React.Fragment key={sub.id}>
                    <tr className={`cursor-pointer transition-colors ${
                      isSmallBusiness(sub) ? 'hover:bg-purple-50 bg-purple-50/30' : 'hover:bg-gray-50'
                    }`}
                      onClick={() => setExpandedId(expandedId === sub.id ? null : sub.id)}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {isSmallBusiness(sub) && <span className="text-purple-600 text-xs" title="Small Business">⭐</span>}
                          <div>
                            <div className="font-medium text-gray-900">{sub.company_name}</div>
                            {sub.website && (
                              <a href={sub.website} target="_blank" rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:underline"
                                onClick={e => e.stopPropagation()}>
                                {sub.website.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]}
                              </a>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {sub.service_type || <span className="text-gray-400">—</span>}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {[sub.city, sub.state].filter(Boolean).join(', ') || <span className="text-gray-400">—</span>}
                      </td>
                      <td className="px-4 py-3">
                        {(sub.socioeconomic_certs || []).length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {sub.socioeconomic_certs.map(c => (
                              <span key={c} className={`px-1.5 py-0.5 text-xs font-medium rounded ${certBadge(c)}`}>
                                {c}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-400 text-xs">None</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {sub.relationship_status ? (
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRelStatusColor(sub.relationship_status)}`}>
                            {sub.relationship_status}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-xs">Unknown</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {renderStars(sub.reliability_rating)}
                      </td>
                    </tr>

                    {/* Expanded Detail Row */}
                    {expandedId === sub.id && (
                      <tr className="bg-gray-50">
                        <td colSpan={6} className="px-4 py-4">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Col 1: Contact & Details */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-gray-900 text-sm">Contact & Details</h4>
                              <div className="text-xs space-y-1 text-gray-600">
                                {sub.email && (
                                  <div>
                                    <span className="font-medium">Email:</span>{' '}
                                    <a href={`mailto:${sub.email}`} className="text-blue-600 hover:underline"
                                      onClick={e => e.stopPropagation()}>{sub.email}</a>
                                  </div>
                                )}
                                {sub.phone && (
                                  <div>
                                    <span className="font-medium">Phone:</span>{' '}
                                    <a href={`tel:${sub.phone}`} className="text-blue-600 hover:underline"
                                      onClick={e => e.stopPropagation()}>{sub.phone}</a>
                                  </div>
                                )}
                                <div><span className="font-medium">Discovered:</span> {sub.discovery_date || 'Unknown'} via {sub.discovery_method || 'Unknown'}</div>
                                <div><span className="font-medium">Last Contacted:</span> {sub.last_contacted || 'Never'}</div>
                                {sub.contracts_won > 0 && (
                                  <div><span className="font-medium">Contracts Won Together:</span> {sub.contracts_won}</div>
                                )}
                                {sub.response_rate > 0 && (
                                  <div><span className="font-medium">Response Rate:</span> {sub.response_rate}%</div>
                                )}
                              </div>
                              {sub.description && (
                                <div className="text-xs text-gray-700 bg-white p-2 rounded border">
                                  {sub.description}
                                </div>
                              )}
                            </div>

                            {/* Col 2: Business Profile */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-gray-900 text-sm">Business Profile</h4>
                              <div className="text-xs space-y-1 text-gray-600">
                                {sub.employee_count > 0 && (
                                  <div><span className="font-medium">Employees:</span> {sub.employee_count}</div>
                                )}
                                {sub.annual_revenue > 0 && (
                                  <div><span className="font-medium">Annual Revenue:</span> ${(sub.annual_revenue / 1000000).toFixed(1)}M</div>
                                )}
                                {sub.hourly_rates && (
                                  <div><span className="font-medium">Rates:</span> {sub.hourly_rates}</div>
                                )}
                                {sub.availability && (
                                  <div><span className="font-medium">Availability:</span>{' '}
                                    <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                                      sub.availability === 'AVAILABLE' ? 'bg-green-100 text-green-800' :
                                      sub.availability === 'BUSY' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-red-100 text-red-800'
                                    }`}>{sub.availability}</span>
                                  </div>
                                )}
                                {sub.compliance_risk && (
                                  <div><span className="font-medium">Compliance Risk:</span>{' '}
                                    <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                                      sub.compliance_risk === 'LOW' ? 'bg-green-100 text-green-800' :
                                      sub.compliance_risk === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-red-100 text-red-800'
                                    }`}>{sub.compliance_risk}</span>
                                  </div>
                                )}
                              </div>
                              {(sub.capabilities || []).length > 0 && (
                                <div>
                                  <div className="text-xs font-medium text-gray-700 mb-1">Capabilities:</div>
                                  <div className="flex flex-wrap gap-1">
                                    {sub.capabilities.map(c => (
                                      <span key={c} className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">{c}</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {(sub.naics_codes || []).length > 0 && (
                                <div>
                                  <div className="text-xs font-medium text-gray-700 mb-1">NAICS Codes:</div>
                                  <div className="text-xs text-gray-600">{sub.naics_codes.join(', ')}</div>
                                </div>
                              )}
                              {(sub.primary_agencies || []).length > 0 && (
                                <div>
                                  <div className="text-xs font-medium text-gray-700 mb-1">Primary Agencies:</div>
                                  <div className="text-xs text-gray-600">{sub.primary_agencies.join(', ')}</div>
                                </div>
                              )}
                            </div>

                            {/* Col 3: Actions */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-gray-900 text-sm">Actions</h4>
                              <div className="flex flex-col gap-2">
                                <button onClick={(e) => { e.stopPropagation(); openEdit(sub); }}
                                  className="px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">
                                  Edit Subcontractor
                                </button>
                                {sub.email && (
                                  <a href={`mailto:${sub.email}`} onClick={e => e.stopPropagation()}
                                    className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center">
                                    Email: {sub.email}
                                  </a>
                                )}
                                {sub.phone && (
                                  <a href={`tel:${sub.phone}`} onClick={e => e.stopPropagation()}
                                    className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center">
                                    Call: {sub.phone}
                                  </a>
                                )}
                                {sub.website && (
                                  <a href={sub.website} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
                                    className="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 font-medium text-center">
                                    Visit Website
                                  </a>
                                )}
                              </div>
                              {sub.notes && (
                                <div>
                                  <div className="text-xs font-medium text-gray-700 mb-1">Notes:</div>
                                  <div className="text-xs text-gray-600 bg-white p-2 rounded border">{sub.notes}</div>
                                </div>
                              )}
                              {sub.past_performance && (
                                <div>
                                  <div className="text-xs font-medium text-gray-700 mb-1">Past Performance:</div>
                                  <div className="text-xs text-gray-600 bg-white p-2 rounded border">{sub.past_performance}</div>
                                </div>
                              )}
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
        <div className="px-4 py-2 text-xs text-gray-400 text-right border-t">
          Showing {filtered.length} of {total} subcontractors
        </div>
      </div>

      {/* ============ FIND MODAL ============ */}
      {showFindModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-2">Find Subcontractors</h3>
              <p className="text-sm text-gray-600 mb-4">
                Search Google Maps and web directories for local subcontractors.
                Prioritize very small businesses — they're hungry, responsive, and great partners.
              </p>

              <div className="space-y-4 mb-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Service Type *</label>
                    <input type="text" value={findService}
                      onChange={e => setFindService(e.target.value)}
                      placeholder="lawn care, pressure washing, HVAC, electrical"
                      className="w-full px-3 py-2 border rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
                    <input type="text" value={findLocation}
                      onChange={e => setFindLocation(e.target.value)}
                      placeholder="Oakland County, MI"
                      className="w-full px-3 py-2 border rounded-lg text-sm" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Radius: {findRadius} miles
                  </label>
                  <input type="range" min="5" max="100" value={findRadius}
                    onChange={e => setFindRadius(parseInt(e.target.value))} className="w-full" />
                </div>
                <button onClick={handleFind} disabled={isFinding}
                  className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium disabled:opacity-50">
                  {isFinding ? 'Searching...' : 'Search Now'}
                </button>
              </div>

              {findResults.length > 0 && (
                <div>
                  <h4 className="font-bold mb-2">Found {findResults.length} Subcontractors:</h4>
                  <div className="space-y-2 max-h-80 overflow-y-auto">
                    {findResults.map((r, i) => (
                      <div key={i} className="border rounded-lg p-3 hover:bg-gray-50 flex justify-between items-center">
                        <div>
                          <div className="font-medium text-sm text-gray-900">{r.company_name}</div>
                          <div className="text-xs text-gray-600">
                            {r.phone && <span>{r.phone}</span>}
                            {r.distance && <span className="ml-2">{r.distance.toFixed(1)} mi</span>}
                          </div>
                        </div>
                        <button onClick={() => handleAddFromFind(r)}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 font-medium">
                          + Add
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button onClick={() => { setShowFindModal(false); setFindResults([]); }}
                className="mt-4 w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-sm">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============ ADD/EDIT MODAL ============ */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-xl font-bold mb-4">
                {editingSub ? `Edit: ${editingSub.company_name}` : 'Add Subcontractor'}
              </h3>
              <form onSubmit={handleSave} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
                  <input type="text" required value={formData['Company Name']}
                    onChange={e => setFormData({...formData, 'Company Name': e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
                    <input type="text" value={formData['Service Type']}
                      onChange={e => setFormData({...formData, 'Service Type': e.target.value})}
                      placeholder="Lawn care, HVAC, Electrical..."
                      className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                    <input type="text" value={formData['State']}
                      onChange={e => setFormData({...formData, 'State': e.target.value})}
                      placeholder="MI" className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                    <input type="text" value={formData['City']}
                      onChange={e => setFormData({...formData, 'City': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
                    <input type="url" value={formData['Website']}
                      onChange={e => setFormData({...formData, 'Website': e.target.value})}
                      placeholder="https://" className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" value={formData['Email']}
                      onChange={e => setFormData({...formData, 'Email': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input type="tel" value={formData['Phone']}
                      onChange={e => setFormData({...formData, 'Phone': e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea value={formData['Description']}
                    onChange={e => setFormData({...formData, 'Description': e.target.value})}
                    rows={2} className="w-full px-3 py-2 border rounded-lg"
                    placeholder="What do they do? What makes them a good partner?" />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Employees</label>
                    <input type="number" value={formData['Employee Count'] || ''}
                      onChange={e => setFormData({...formData, 'Employee Count': parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 border rounded-lg" min="0" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Annual Revenue ($)</label>
                    <input type="number" value={formData['Annual Revenue'] || ''}
                      onChange={e => setFormData({...formData, 'Annual Revenue': parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border rounded-lg" min="0" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Hourly Rates</label>
                    <input type="text" value={formData['Hourly Rates']}
                      onChange={e => setFormData({...formData, 'Hourly Rates': e.target.value})}
                      placeholder="$25-45/hr" className="w-full px-3 py-2 border rounded-lg" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea value={formData['Notes']}
                    onChange={e => setFormData({...formData, 'Notes': e.target.value})}
                    rows={2} className="w-full px-3 py-2 border rounded-lg" />
                </div>
                <div className="flex gap-3 pt-4">
                  <button type="submit" disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50">
                    {loading ? 'Saving...' : (editingSub ? 'Update' : 'Add Subcontractor')}
                  </button>
                  <button type="button"
                    onClick={() => { setShowAddModal(false); setEditingSub(null); resetForm(); }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium">
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

export default SubcontractorsTab;
